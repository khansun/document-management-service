import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import NoResultFound

from datetime import datetime, timedelta, UTC
import jwt
from passlib.hash import pbkdf2_sha256

from fastapi import HTTPException
import requests
from papermerge.core.features.auth.db import api as dbapi
from papermerge.core.features.auth.db.orm import User
from papermerge.core.features.auth import schema
from papermerge.core.config import Settings
from papermerge.core.features.auth.utils import raise_on_empty


logger = logging.getLogger(__name__)
settings = Settings()


async def authenticate(
    session: Session,
    *,
    username: str | None = None,
    password: str | None = None,
    provider: schema.AuthProvider = schema.AuthProvider.DB,
    client_id: str | None = None,
    code: str | None = None,
    redirect_url: str | None = None,
) -> schema.User | str | None:

    # provider = DB
    if username and password and provider == schema.AuthProvider.DB:
        # password based authentication against database
        return db_auth(session, username, password)
    else:
        raise ValueError("Unknown or empty auth provider")



def create_access_token(
    data: schema.TokenData,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta | None = None,
) -> str:
    logger.debug(f"create access token for data={data}")

    to_encode = data.model_dump()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=15)
    to_encode.update({"exp": expire})

    try:
        encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    except Exception as exc:
        logger.error(exc)
        raise

    return encoded_jwt


def db_auth(session: Session, username: str, password: str) -> schema.User | None:
    """Authenticates user based on username and password

    User data is read from database.
    """
    logger.info(f"Database based authentication for '{username}'")

    try:
        user: schema.User | None = dbapi.get_user_by_username(session, username)
    except NoResultFound:
        user = None

    if not user:
        logger.warning(f"User {username} not found in database")
        return None, f"User {username} not found in database"

    if not (settings.papermerge__developer__login == "yes"):
        authSuccess, message = external_domain_validation(settings.external__auth__url1, username, password)
        if not authSuccess:
            logger.warning(f"Authentication failed in {settings.external__auth__url1} for '{username}'")
            authSuccess, message = external_domain_validation(settings.external__auth__url2, username, password)
            if not authSuccess:
                logger.warning(f"Authentication failed in {settings.external__auth__url2} for '{username}'")
                return None, message

    logger.info(f"Authentication succeded for '{username}'")

    return user, "OK"

def external_domain_validation(url: str, username: str, password: str) -> bool:
    headers = {
        'Content-Type': 'application/json'
    }
    data = {
        "user_name": username,
        "user_pass": password
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        if result.get("status") == 1:
            return True, "OK"
        else:
            logger.warning(f"Password validation failed for '{username}': {result.get('message')}")
            return False, result.get('message')
    logger.error(f"Error validating password for '{username}': {response.status_code}")
    return False, result.get('message')


def create_token(user: schema.User) -> str:
    access_token_expires = timedelta(
        minutes=settings.papermerge__security__token_expire_minutes
    )
    data = schema.TokenData(
        sub=str(user.id),
        preferred_username=user.username,
        email=user.email,
        scopes=user.scopes,
    )

    access_token = create_access_token(
        data=data,
        expires_delta=access_token_expires,
        secret_key=settings.papermerge__security__secret_key,
        algorithm=settings.papermerge__security__token_algorithm,
    )

    return access_token
