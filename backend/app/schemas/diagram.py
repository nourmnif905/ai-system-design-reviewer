from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class DiagramFormat(str, Enum):
    mermaid = "mermaid"
    plantuml = "plantuml"
    image = "image"


class DiagramCreate(BaseModel):
    format: DiagramFormat
    raw_content: str


class DiagramOut(BaseModel):
    id: int
    project_id: int
    format: DiagramFormat
    raw_content: str
    parsed_structure: str | None
    created_at: datetime

    class Config:
        from_attributes = True
