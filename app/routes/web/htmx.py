from fastapi import APIRouter, Depends, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.routes.api.deps import get_db
from app.routes.web.auth import get_current_user_optional
from app.services.user_service import list_users
from app.services import project_service
from app.services.board_service import get_board_data
from app.services.task_service import create_task, soft_delete_task, move_task, update_task
from app.services.column_service import create_column, update_column, soft_delete_column

templates = Jinja2Templates(directory="app/templates")
router = APIRouter(prefix="/htmx", tags=["htmx"])


def _require_user(request: Request, db: Session):
    user = get_current_user_optional(request, db)
    if not user:
        return None, HTMLResponse("", status_code=401, headers={"HX-Redirect": "/login"})
    return user, None


@router.post("/projects", response_class=HTMLResponse)
def htmx_create_project(
    request: Request,
    assignee_id: int | None = Form(None),
    title: str = Form(...),
    description: str | None = Form(None),
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    project = project_service.create_project(db, user_id=user.id, title=title, description=description)
    return templates.TemplateResponse("partials/project_card.html", {"request": request, "project": project})


@router.delete("/projects/{project_id}", response_class=HTMLResponse)
def htmx_delete_project(project_id: int, request: Request, db: Session = Depends(get_db)):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    ok = project_service.soft_delete_project(db, project_id=project_id, user_id=user.id)
    if not ok:
        raise HTTPException(status_code=404, detail="Project not found")
    # برگرد به داشبورد
    return HTMLResponse("", headers={"HX-Redirect": "/dashboard"})



@router.get("/projects/{project_id}/board", response_class=HTMLResponse)
def htmx_load_board(project_id: int, request: Request, db: Session = Depends(get_db)):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    data = get_board_data(db, project_id=project_id, user_id=user.id)
    if not data:
        raise HTTPException(status_code=404, detail="Board not found")
    return templates.TemplateResponse("partials/board_columns.html", {"request": request, "board": data})


@router.post("/projects/{project_id}/tasks", response_class=HTMLResponse)
def htmx_create_task(
    project_id: int,
    request: Request,
    column_id: int = Form(...),
    assignee_id: int | None = Form(None),
    title: str = Form(...),
    description: str | None = Form(None),
    priority: int = Form(2),
    due_date: str | None = Form(None),
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    from datetime import datetime
    parsed_due = None
    if due_date:
        try:
            parsed_due = datetime.strptime(due_date, "%Y-%m-%d").date()
        except Exception:
            parsed_due = None

    task = create_task(
        db=db,
        project_id=project_id,
        user_id=user.id,
        column_id=column_id,
        assignee_id=assignee_id,
        title=title,
        description=description,
        priority=int(priority),
        due_date=parsed_due,
    )
    if not task:
        raise HTTPException(status_code=400, detail="Invalid data")
    users = list_users(db)
    return templates.TemplateResponse("partials/task_card.html", {"request": request, "task": task, "users": users})


@router.delete("/tasks/{task_id}", response_class=HTMLResponse)
def htmx_delete_task(task_id: int, request: Request, db: Session = Depends(get_db)):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    task = soft_delete_task(db, task_id=task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    # حذف از DOM: hx-swap=outerHTML و خروجی خالی
    return HTMLResponse("")


@router.put("/tasks/{task_id}", response_class=HTMLResponse)
def htmx_update_task(
    task_id: int,
    request: Request,
    assignee_id: int | None = Form(None),
    title: str = Form(...),
    description: str | None = Form(None),
    priority: int = Form(2),
    due_date: str | None = Form(None),
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    from datetime import datetime
    parsed_due = None
    if due_date:
        try:
            parsed_due = datetime.strptime(due_date, "%Y-%m-%d").date()
        except Exception:
            parsed_due = None

    task = update_task(
        db=db,
        task_id=task_id,
        assignee_id=assignee_id,
        title=title,
        description=description,
        priority=int(priority),
        due_date=parsed_due,
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    users = list_users(db)
    return templates.TemplateResponse("partials/task_card.html", {"request": request, "task": task, "users": users})



@router.put("/tasks/{task_id}/move", response_class=HTMLResponse)
def htmx_move_task(
    task_id: int,
    request: Request,
    to_column_id: int = Form(...),
    order: str = Form(...),  # comma separated ids
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    try:
        order_ids = [int(x) for x in order.split(",") if x.strip()]
    except Exception:
        order_ids = []
    task = move_task(db, task_id=task_id, to_column_id=to_column_id, order_ids=order_ids)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    users = list_users(db)
    return templates.TemplateResponse("partials/task_card.html", {"request": request, "task": task, "users": users})


@router.post("/projects/{project_id}/columns", response_class=HTMLResponse)
def htmx_create_column(
    project_id: int,
    request: Request,
    assignee_id: int | None = Form(None),
    title: str = Form(...),
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    col = create_column(db, project_id=project_id, user_id=user.id, title=title)
    if not col:
        raise HTTPException(status_code=400, detail="Invalid data")
    users = list_users(db)
    return templates.TemplateResponse("partials/column_card.html", {"request": request, "column": col, "project_id": project_id, "users": users})


@router.put("/projects/{project_id}/columns/{column_id}", response_class=HTMLResponse)
def htmx_update_column(
    project_id: int,
    column_id: int,
    request: Request,
    assignee_id: int | None = Form(None),
    title: str = Form(...),
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    col = update_column(db, column_id=column_id, title=title)
    if not col:
        raise HTTPException(status_code=404, detail="Column not found")
    # ساده: پس از تغییر، کل برد مجدد لود می‌شود (سمت کلاینت)
    return HTMLResponse("")


@router.delete("/projects/{project_id}/columns/{column_id}", response_class=HTMLResponse)
def htmx_delete_column(
    project_id: int,
    column_id: int,
    request: Request,
    db: Session = Depends(get_db),
):
    user, resp = _require_user(request, db)
    if resp:
        return resp
    ok = soft_delete_column(db, project_id=project_id, column_id=column_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Column not found")
    return HTMLResponse("")
