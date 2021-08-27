import os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker

# Ref: https://towardsdatascience.com/build-an-async-python-service-with-fastapi-sqlalchemy-196d8792fa08

SQLALCHEMY_BINDS = {
    'temp': create_async_engine(
        f'sqlite+aiosqlite:///{os.path.join(os.getcwd(), "data", "temp_local.db")}',
        connect_args={"check_same_thread": False},
        echo=True, logging_name='sqlalchemy', future=True  # TODO: Mudar o echo para False
        ),
    'data': create_async_engine(
        f'sqlite+aiosqlite:///{os.path.join(os.getcwd(), "data", "data_local.db")}',
        connect_args={"check_same_thread": False},
        echo=True, logging_name='sqlalchemy', future=True  # TODO: Mudar o echo para False
        )
}

temp_session = sessionmaker(autocommit=False, autoflush=False, bind=SQLALCHEMY_BINDS['temp'], class_=AsyncSession)
data_session = sessionmaker(autocommit=False, autoflush=False, bind=SQLALCHEMY_BINDS['data'], class_=AsyncSession)
