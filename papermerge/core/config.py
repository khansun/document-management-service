from enum import Enum

from pathlib import Path

from pydantic_settings import BaseSettings
import logging


logger = logging.getLogger(__name__)
class FileServer(str, Enum):
    LOCAL = 'local'
    S3 = 's3'


class Algs(str, Enum):
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    ES256 = "ES256"
    ES384 = "ES384"
    ES512 = "ES512"
    
class Settings(BaseSettings):
    papermerge__main__logging_cfg: Path | None = Path("/etc/papermerge/logging.yaml")
    papermerge__main__media_root: Path = Path("media")
    papermerge__main__api_prefix: str = ''
    papermerge__main__file_server: FileServer = FileServer.LOCAL
    papermerge__main__cf_sign_url_private_key: str | None = None
    papermerge__main__cf_sign_url_key_id: str | None = None
    papermerge__main__cf_domain: str | None = None
    papermerge__database__url: str = "sqlite:////db/db.sqlite3"
    papermerge__redis__url: str | None = None
    papermerge__ocr__default_language: str = 'deu'
    papermerge__search__url: str | None = None
    papermerge__security__secret_key: str
    papermerge__security__token_algorithm: Algs = Algs.HS256
    papermerge__security__token_expire_minutes: int = 60
    papermerge__security__cookie_name: str = "access_token"
    papermerge__index__interval__seconds: int = 60
    papermerge__developer__login: str = 'no'
    external__auth__url1: str | None = None
    external__auth__url2: str | None = None   

settings = Settings()


def get_settings():
    return settings
