from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.csrf import create_csrf_token, verify_csrf_token
from app.core.database import get_db
from app.core.deps import get_current_user_from_cookie
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.entities import Board, Column, Task, User, UserRole

router = APIRouter(tags=['ui'])
templates = Jinja2Templates(directory='app/templates')


@router.get('/', response_class=HTMLResponse)
def root() -> RedirectResponse:
    return RedirectResponse('/login')


@router.get('/login', response_class=HTMLResponse)
def login_page(request: Request):
    csrf_session = request.cookies.get('csrf_session') or 'anon'
    csrf_token = create_csrf_token(csrf_session)
    response = templates.TemplateResponse('auth/login.html', {'request': request, 'csrf_token': csrf_token})
    if 'csrf_session' not in request.cookies:
        response.set_cookie('csrf_session', 'anon', httponly=True, samesite='lax', secure=False)
    return response


@router.post('/login', response_class=HTMLResponse)
def login_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
):
    csrf_session = request.cookies.get('csrf_session', 'anon')
    if not verify_csrf_token(csrf_token, csrf_session):
        raise HTTPException(status_code=403, detail='CSRF token نامعتبر است')

    user = db.scalar(select(User).where(User.username == username))
    if not user or not verify_password(password, user.password_hash):
        return templates.TemplateResponse(
            'auth/login.html',
            {'request': request, 'error': 'نام کاربری یا رمز عبور اشتباه است', 'csrf_token': create_csrf_token(csrf_session)},
            status_code=401,
        )

    token = create_access_token(str(user.id))
    res = RedirectResponse('/dashboard', status_code=303)
    res.set_cookie('access_token', token, httponly=True, samesite='lax', secure=False)
    res.set_cookie('csrf_session', str(user.id), httponly=True, samesite='lax', secure=False)
    return res


@router.get('/register', response_class=HTMLResponse)
def register_page(request: Request):
    csrf_session = request.cookies.get('csrf_session') or 'anon'
    return templates.TemplateResponse(
        'auth/register.html', {'request': request, 'csrf_token': create_csrf_token(csrf_session)}
    )


@router.post('/register', response_class=HTMLResponse)
def register_form(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
    csrf_token: str = Form(...),
):
    csrf_session = request.cookies.get('csrf_session', 'anon')
    if not verify_csrf_token(csrf_token, csrf_session):
        raise HTTPException(status_code=403, detail='CSRF token نامعتبر است')

    if len(password) < 8:
        return templates.TemplateResponse(
            'auth/register.html',
            {'request': request, 'error': 'رمز عبور باید حداقل ۸ کاراکتر باشد', 'csrf_token': create_csrf_token(csrf_session)},
            status_code=400,
        )
    existing = db.scalar(select(User).where(User.username == username))
    if existing:
        return templates.TemplateResponse(
            'auth/register.html',
            {'request': request, 'error': 'نام کاربری تکراری است', 'csrf_token': create_csrf_token(csrf_session)},
            status_code=409,
        )

    role = UserRole.admin if db.query(User).count() == 0 else UserRole.user
    user = User(username=username, password_hash=get_password_hash(password), role=role)
    db.add(user)
    db.commit()
    return RedirectResponse('/login', status_code=303)


@router.post('/logout')
def logout() -> RedirectResponse:
    response = RedirectResponse('/login', status_code=303)
    response.delete_cookie('access_token')
    return response


@router.get('/dashboard', response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_from_cookie)):
    boards_q = select(Board)
    if current_user.role != UserRole.admin:
        boards_q = boards_q.where(Board.owner_id == current_user.id)
    boards = db.scalars(boards_q).all()

    board_data = []
    for board in boards:
        columns = db.scalars(select(Column).where(Column.board_id == board.id)).all()
        column_ids = [c.id for c in columns]
        tasks = db.scalars(select(Task).where(Task.column_id.in_(column_ids))).all() if column_ids else []
        grouped_tasks: dict[int, list[Task]] = {c.id: [] for c in columns}
        for task in tasks:
            grouped_tasks[task.column_id].append(task)
        columns_data = [{'column': col, 'tasks': grouped_tasks.get(col.id, [])} for col in columns]
        board_data.append({'board': board, 'columns': columns_data})

    return templates.TemplateResponse(
        'dashboard.html',
        {
            'request': request,
            'user': current_user,
            'board_data': board_data,
            'csrf_token': create_csrf_token(str(current_user.id)),
        },
    )


@router.post('/preferences/theme')
def set_theme(
    request: Request,
    enabled: int = Form(0),
    csrf_token: str = Form(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie),
):
    if not verify_csrf_token(csrf_token, str(current_user.id)):
        raise HTTPException(status_code=403, detail='CSRF token نامعتبر است')
    current_user.dark_mode = bool(enabled)
    db.commit()
    return {'ok': True}
