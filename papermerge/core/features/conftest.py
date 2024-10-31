import uuid

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from papermerge.core import constants
from papermerge.core.auth.scopes import SCOPES
from papermerge.core.db import models as orm
from papermerge.core.db.base import Base
from papermerge.core.db.engine import Session, engine
from papermerge.core.features.custom_fields import router as cf_router
from papermerge.core.features.custom_fields.db import api as cf_dbapi
from papermerge.core.features.custom_fields.schema import CustomFieldType
from papermerge.core.features.document_types import router as document_types_router
from papermerge.core.features.document_types.db import api as dt_dbapi
from papermerge.core.features.groups import router as groups_router
from papermerge.core.utils import base64
from papermerge.test.types import AuthTestClient


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(engine)
    with Session() as session:
        yield session

    Base.metadata.drop_all(engine)


@pytest.fixture()
def auth_api_client(user: orm.User):
    app = FastAPI()
    app.include_router(document_types_router.router, prefix="")
    app.include_router(groups_router.router, prefix="")
    app.include_router(cf_router.router, prefix="")

    middle_part = base64.encode(
        {
            "sub": str(user.id),
            "preferred_username": user.username,
            "email": user.email,
            "scopes": list(SCOPES.keys()),
        }
    )
    token = f"abc.{middle_part}.xyz"

    test_client = TestClient(app, headers={"Authorization": f"Bearer {token}"})

    return AuthTestClient(test_client=test_client, user=user)


@pytest.fixture()
def user(make_user) -> orm.User:
    return make_user(username="random")


@pytest.fixture()
def make_user(db_session: Session):
    def _maker(username: str, is_superuser: bool = True):
        user_id = uuid.uuid4()
        home_id = uuid.uuid4()
        inbox_id = uuid.uuid4()

        db_user = orm.User(
            id=user_id,
            username=username,
            email=f"{username}@mail.com",
            first_name=f"{username}_first",
            last_name=f"{username}_last",
            is_superuser=is_superuser,
            is_active=True,
            password="pwd",
        )
        db_inbox = orm.Folder(
            id=inbox_id,
            title=constants.INBOX_TITLE,
            ctype=constants.CTYPE_FOLDER,
            lang="de",
            user_id=user_id,
        )
        db_home = orm.Folder(
            id=home_id,
            title=constants.HOME_TITLE,
            ctype=constants.CTYPE_FOLDER,
            lang="de",
            user_id=user_id,
        )
        db_session.add(db_inbox)
        db_session.add(db_home)
        db_session.add(db_user)
        db_session.commit()
        db_user.home_folder_id = db_home.id
        db_user.inbox_folder_id = db_inbox.id
        db_session.commit()

        return db_user

    return _maker


@pytest.fixture
def document_type_groceries(db_session: Session, user, make_custom_field):
    cf1 = make_custom_field(name="Shop", type=CustomFieldType.text)
    cf2 = make_custom_field(name="Total", type=CustomFieldType.monetary)
    cf3 = make_custom_field(name="EffectiveDate", type=CustomFieldType.date)

    return dt_dbapi.create_document_type(
        db_session,
        name="Groceries",
        custom_field_ids=[cf1.id, cf2.id, cf3.id],
        user_id=user.id,
    )


@pytest.fixture
def make_custom_field(db_session: Session, user):
    def _make_custom_field(name: str, type: CustomFieldType):
        return cf_dbapi.create_custom_field(
            db_session,
            name=name,
            type=type,
            user_id=user.id,
        )

    return _make_custom_field
