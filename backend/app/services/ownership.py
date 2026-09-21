from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.project import Project


def get_owned_project_or_404(
    project_id: int, current_user: User, db: Session
) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable."
        )

    if project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Projet introuvable."
        )

    return project
