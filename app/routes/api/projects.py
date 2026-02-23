from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.routes.api.deps import get_db, DEFAULT_USER_ID
from app.schemas.project import ProjectCreate, ProjectOut, ProjectUpdate
from app.services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return project_service.list_projects(db, user_id=DEFAULT_USER_ID)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    return project_service.create_project(db, user_id=DEFAULT_USER_ID, title=payload.title, description=payload.description)


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id=project_id, user_id=DEFAULT_USER_ID)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = project_service.get_project(db, project_id=project_id, user_id=DEFAULT_USER_ID)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if payload.title is not None:
        project.title = payload.title
    if payload.description is not None:
        project.description = payload.description

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    ok = project_service.soft_delete_project(db, project_id=project_id, user_id=DEFAULT_USER_ID)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    return {"ok": True}
