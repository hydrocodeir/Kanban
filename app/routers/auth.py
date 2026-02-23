from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import check_login_rate_limit, get_user_by_username
from app.core.security import create_access_token, decode_token, get_password_hash, verify_password
from app.models.entities import User, UserRole
from app.schemas.api import TokenResponse, UserCreate, UserOut
from app.services.activity import log_action

router = APIRouter(prefix='/api/auth', tags=['auth'])


@router.post('/register', response_model=UserOut)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    if get_user_by_username(db, payload.username):
        raise HTTPException(status_code=409, detail='نام کاربری تکراری است')
    role = UserRole.admin if db.query(User).count() == 0 else UserRole.user
    user = User(username=payload.username, password_hash=get_password_hash(payload.password), role=role)
    db.add(user)
    db.commit()
    db.refresh(user)
    log_action(db, user.id, 'register', 'user', user.id)
    return user


@router.post('/login', response_model=TokenResponse)
def login(
    request: Request,
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    check_login_rate_limit(request)
    user = get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail='نام کاربری یا رمز عبور اشتباه است')
    token = create_access_token(str(user.id))
    response.set_cookie('access_token', token, httponly=True, samesite='lax', secure=False)
    log_action(db, user.id, 'login', 'user', user.id)
    return TokenResponse(access_token=token)


@router.post('/logout')
def logout(response: Response, db: Session = Depends(get_db), request: Request | None = None):
    token = request.cookies.get('access_token') if request else None
    if token:
        user_id = decode_token(token)
        if user_id:
            log_action(db, int(user_id), 'logout', 'user', int(user_id))
    response.delete_cookie('access_token')
    return {'message': 'خروج با موفقیت انجام شد'}
