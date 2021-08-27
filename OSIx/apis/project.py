"""Projects API."""
from typing import List
from fastapi import APIRouter
from models.apis.project import ProjectResponse

router = APIRouter()

@router.get(
    path="/",
    response_model=ProjectResponse,
    responses={404: {"description": "Theres No Projects"}}, tags=["project"]
    )
async def list_projects():
    """List all Projects."""

    return {"q_or_cookie": 12}

@router.get(
    path="/{project_id}/",
    response_model=List[ProjectResponse],
    responses={404: {"description": "Project not Found"}}
    )
async def list_projects(project_id: str):
    """
    Get a Single Project Informations.

    :param project_id: Project Identification
    :return:
    """
    return {"q_or_cookie": project_id}