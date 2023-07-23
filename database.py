from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import make_url

import platform_consts as Const

url = make_url(Const.DATABASE_STRING)
_engine_kw_args = (
    {"connect_args": {"check_same_thread": False}}
    if "sqlite" in url.get_backend_name()
    else {
        "pool_size": Const.DATABASE_POOL_SIZE,
        "max_overflow": Const.DATABASE_POOL_OVERFLOW_SIZE,
        "pool_timeout": Const.DATABASE_POOL_TIMEOUT,
    }
)
"""Address #19 - add additional engine args for sqlite exclusively.
https://github.com/City-Now-LT/Challenge_WEB_Backend/issues/19"""

engine = create_engine(url, **_engine_kw_args)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _get_db_context():
    return SessionLocal()


def proxy_get_db_context() -> callable:
    return _get_db_context
