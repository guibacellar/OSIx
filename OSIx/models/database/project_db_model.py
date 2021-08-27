"""Projects DB Models."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

ProjectDataBaseDeclarativeBase = declarative_base()


class ProjectOrmEntiry(ProjectDataBaseDeclarativeBase):
    """Temporary Data ORM Model."""

    __bind_key__ = 'data'
    __tablename__ = 'project'

    pk: str = Column(String(255), primary_key=True)
    name: str = Column(String(255))  # TODO: Fix
    target: str = Column(String(255))  # TODO: Fix
    type: str  = Column(String(255))  # TODO: Fix
