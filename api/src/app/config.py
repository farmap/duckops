import os
import pathlib
from functools import lru_cache
from dotenv import load_dotenv

from urllib.parse import quote

from app.utils import process_boolean_str, parent_dir
basedir = os.path.abspath(os.path.dirname(__file__))
rootdir = parent_dir(basedir, levels=3)
load_dotenv()


class BaseConfig:
    BASE_DIR: pathlib.Path = pathlib.Path(__file__).parent.parent
    INSTANCE_DIR: str = os.environ.get("INSTANCE_DIR", "instance")
    DATABASE_URL: str = os.environ.get("DATABASE_URL", f"sqlite:///{BASE_DIR}/{INSTANCE_DIR}/db.sqlite3")
    DATABASE_CONNECT_DICT: dict = {'check_same_thread': False}
    FASTAPI_DEBUG: bool = process_boolean_str(os.environ.get('FASTAPI_DEBUG') or 'true')



class DevelopmentConfig(BaseConfig):
    pass


class ProductionConfig(BaseConfig):
    PSQL_HOST = os.environ.get('PSQL_HOST') or 'localhost'
    PSQL_PORT = os.environ.get('PSQL_PORT') or '5432'
    PSQL_DATABASE = os.environ.get('PSQL_DATABASE') or 'phildemo'
    PSQL_USER = os.environ.get('PSQL_USER') or 'postgres'
    PSQL_PASS = os.environ.get('PSQL_PASS')

    DATABASE_URL: str = os.environ.get('DATABASE_URL') or \
                        "postgresql://{}:{}@{}:{}/{}".format(PSQL_USER, PSQL_PASS, PSQL_HOST, PSQL_PORT,
                                                             PSQL_DATABASE)
    DATABASE_CONNECT_DICT: dict = {"connect_timeout": 5}
    FASTAPI_DEBUG: bool = process_boolean_str(os.environ.get('FASTAPI_DEBUG') or 'false')


class TestingConfig(BaseConfig):
    pass


@lru_cache()
def get_settings():
    config_cls_dict = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "testing": TestingConfig
    }

    config_name = os.environ.get("FASTAPI_CONFIG", "development")
    config_cls = config_cls_dict[config_name]
    return config_cls()


settings = get_settings()
