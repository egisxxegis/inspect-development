# this module will be imported numerous times, so let us
# prefix internal stuff with symbol _ (underscore)
import os as _os
from datetime import timedelta as _timedelta

from dotenv import load_dotenv as _load_dotenv

_load_dotenv()  # load env vars from .env


HOST = _os.environ["HOST_ON"].strip()
"""Where to host this program."""

PORT = int(_os.environ["LISTEN_ON_PORT"].strip())
"""On what port to listen for outside-requests."""

DATABASE_STRING = _os.environ["DATABASE_LOGIN_STRING"].strip()
"""The database login url which has data about user, password, database, etc. Format depends on used DB system."""

DATABASE_POOL_SIZE = int(_os.environ["DATABASE_POOL_SIZE"].strip())
"""How many connections to DB are to be always opened? P.s. usually DB supports < 100 connections"""

DATABASE_POOL_OVERFLOW_SIZE = int(_os.environ["DATABASE_POOL_OVERFLOW_SIZE"].strip())
"""How many connections to DB open on demand when POOL gets exhausted?"""

DATABASE_POOL_TIMEOUT = int(_os.environ["DATABASE_POOL_TIMEOUT_IN_S"].strip())
"""How much seconds to wait when no connection to DB can be retrieved / opened?"""

SQL_SLEEP_SECONDS = 10
"""How long to sleep in query if SQL server supports it?"""

LOGGING_LEVEL = "INFO"
"""What is the level of logging"""

LOGGING_FORMAT = _os.environ["LOG_FORMAT"].strip()
"""Format of logging message"""
