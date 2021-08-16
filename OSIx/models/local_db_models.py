"""Temporary Data Model."""

from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from OSIx.database.local_db import LOCAL_DB_INSTANCE


Base = declarative_base()


class TempDataOrmEntity(Base):
    """Temporary Data ORM Model."""

    __tablename__ = 'temporary_data'

    path = Column(String(255), primary_key=True)
    module = Column(String(255))
    data = Column(String)
    created_at = Column(Integer)
    valid_at = Column(Integer)


class StateFileOrmEntity(Base):
    """Temporary Data ORM Model."""

    __tablename__ = 'state_file'

    path = Column(String(255), primary_key=True)
    data = Column(String)
    created_at = Column(Integer)


Base.metadata.create_all(LOCAL_DB_INSTANCE.local_db_engine)
