from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routes.api.deps import get_db
from app.routes.web.auth import get_current_user_optional
from app.services import project_service

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()


@router.get("/", include_in_schema=False)
def root():
    return RedirectResponse(url="/dashboard", status_code=302)


@router.get("/dashboard", include_in_schema=False)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    projects = project_service.list_projects(db, user_id=user.id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "projects": projects, "user": user})


@router.get("/projects/{project_id}", include_in_schema=False)
def project_board_page(project_id: int, request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if not user:
        return RedirectResponse(url='/login', status_code=303)
    project = project_service.get_project(db, project_id=project_id, user_id=user.id)
    return templates.TemplateResponse("board.html", {"request": request, "project": project, "user": user})
