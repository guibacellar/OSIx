"""Local Database Manager."""

import os

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import session, sessionmaker


class LocalDatabaseManager:
    """Local Database Manager."""

    def __init__(self):
        """Initialize the Local DB Manager."""

        self.local_db_engine: Engine = create_engine(f'sqlite:///{os.path.join(os.getcwd(), "data", "local.db")}', echo=False, logging_name='sqlalchemy')
        self.local_db_session: session = sessionmaker(bind=self.local_db_engine)()


LOCAL_DB_INSTANCE: LocalDatabaseManager = LocalDatabaseManager()
