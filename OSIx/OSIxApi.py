import io

from fastapi import FastAPI, Response, Request
from apis import project
from database import SQLALCHEMY_BINDS, temp_session, data_session
from models.database.temp_db_models import TempDataBaseDeclarativeBase
from models.database.project_db_model import ProjectDataBaseDeclarativeBase

# Set Documentation Metadata
tags_metadata = [
    {
        "name": "project",
        "description": "Manage Projects."
    },
]

# Initialize the FastAPI
app = FastAPI(
    title="OSIx",
    description="Open Source Intelligence eXplorer",
    version=open('../__version__.txt').read(),
    terms_of_service="https://github.com/guibacellar/OSIx",
    contact={
        "name": "Th3 0bservator",
        "url": "https://github.com/guibacellar/OSIx"
    },
    license_info={
        "name": "Apache 2.0",
        "url": "https://github.com/guibacellar/OSIx/blob/develop/LICENSE",
    },
    openapi_tags=tags_metadata
)

# Register all Routes
app.include_router(
    project.router,
    prefix="/project",
    tags=["project"],
    dependencies=[],
    responses={},
)

# Set Main Database Bindings
@app.on_event("startup")
async def startup():
    # create db tables
    async with SQLALCHEMY_BINDS['temp'].begin() as conn:
        await conn.run_sync(TempDataBaseDeclarativeBase.metadata.create_all)

    async with SQLALCHEMY_BINDS['data'].begin() as conn:
        await conn.run_sync(ProjectDataBaseDeclarativeBase.metadata.create_all)

# TODO: Here, Call Modules to Bind

# TODO: Separar esse Middleware aqui
# Middlewares
@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response: Response = Response("Internal server error", status_code=500)

    try:
        request.state.temp_db = temp_session()
        request.state.data = data_session()

        response = await call_next(request)

        request.state.temp_db.commit()
        request.state.data.commit()
    except:
        request.state.temp_db.rollback()
        request.state.data.rollback()

    finally:
        request.state.temp_db.close()
        request.state.data.close()

    return response
