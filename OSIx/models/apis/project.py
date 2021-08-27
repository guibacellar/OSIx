"""Project Api Models."""

import enum
from pydantic import BaseModel


class ProjectType(str, enum.Enum):
    """Defines the Project Type."""

    BITCOIN_WALLET = 'BITCOIN_WALLET'
    USERNAME = 'USERNAME'
    EMAIL = 'EMAIL'


class ProjectResponse(BaseModel):
    """Defines a Single Project."""

    id: str
    """Project Unique ID."""

    name: str
    """Project Name."""

    target: str
    """Project Target."""

    type: ProjectType
    """Project Type."""

