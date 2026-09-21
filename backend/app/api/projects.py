from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectOut
from app.services.auth_dependency import get_current_user
from app.services.ownership import get_owned_project_or_404

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    project_in: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_project = Project(
        name=project_in.name,
        description=project_in.description,
        owner_id=current_user.id,
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get("", response_model=list[ProjectOut])
def list_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return db.query(Project).filter(Project.owner_id == current_user.id).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_owned_project_or_404(project_id, current_user, db)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    project = get_owned_project_or_404(project_id, current_user, db)
    db.delete(project)
    db.commit()
    return None
