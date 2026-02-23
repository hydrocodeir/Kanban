from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.routes.api.deps import get_db
from app.services import user_service
templates = Jinja2Templates(directory="app/templates")
router = APIRouter(tags=["auth"])


from app.models.user import User


def get_current_user_optional(request: Request, db: Session) -> User | None:
    user_id = request.session.get("user_id")
    if not user_id:
        return None
    return user_service.get_user(db, int(user_id))


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth/login.html", {"request": request, "title": "ورود", "error": None})


@router.post("/login")
def login_submit(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db),
):
    user = user_service.authenticate(db, email=email, password=password)
    if not user:
        return templates.TemplateResponse("auth/login.html", {"request": request, "title": "ورود", "error": "ایمیل یا رمز عبور نادرست است."}, status_code=400)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/register", response_class=HTMLResponse)
def register_page(request: Request, db: Session = Depends(get_db)):
    user = get_current_user_optional(request, db)
    if user:
        return RedirectResponse(url="/dashboard", status_code=303)
    return templates.TemplateResponse("auth/register.html", {"request": request, "title": "ثبت‌نام", "error": None})


@router.post("/register")
def register_submit(
    request: Request,
    full_name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    password2: str = Form(...),
    db: Session = Depends(get_db),
):
    if password != password2:
        return templates.TemplateResponse("auth/register.html", {"request": request, "title": "ثبت‌نام", "error": "تکرار رمز عبور با رمز عبور یکسان نیست."}, status_code=400)
    if len(password) < 6:
        return templates.TemplateResponse("auth/register.html", {"request": request, "title": "ثبت‌نام", "error": "رمز عبور باید حداقل ۶ کاراکتر باشد."}, status_code=400)

    email_norm = email.strip().lower()
    if user_service.get_user_by_email(db, email=email_norm):
        return templates.TemplateResponse("auth/register.html", {"request": request, "title": "ثبت‌نام", "error": "این ایمیل قبلاً ثبت شده است."}, status_code=400)

    user = user_service.create_user(db, full_name=full_name, email=email_norm, password=password)
    request.session["user_id"] = user.id
    return RedirectResponse(url="/dashboard", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/login", status_code=303)
