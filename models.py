import itertools
from datetime import datetime, timedelta
from typing import Any, Iterable

from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
    Table,
    DateTime,
    Enum,
    Float,
    ForeignKeyConstraint,
    false,
    true,
    Index,
)
from sqlalchemy.orm import relationship, Query, Session, deferred

from database import Base
import platform_consts as Const


# nullable=True by default


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)


class Message(Base):
    __tablename__ = "message"

    id = Column(Integer, nullable=False, primary_key=True)
    user_id = Column(ForeignKey("user.id"), nullable=False)
    content = Column(String, nullable=False)
    moderator_id = Column(ForeignKey("user.id"), nullable=True)
