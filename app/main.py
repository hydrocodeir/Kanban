from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import Base, engine
from app.routers import auth, boards, columns, logs, tasks, ui, users

Base.metadata.create_all(bind=engine)

app = FastAPI(title='سامانه کانبان سازمانی')
app.mount('/static', StaticFiles(directory='app/static'), name='static')


@app.middleware('http')
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = "default-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com https://fonts.googleapis.com https://fonts.gstatic.com"
    return response


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(boards.router)
app.include_router(columns.router)
app.include_router(tasks.router)
app.include_router(logs.router)
app.include_router(ui.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={'detail': 'خطای داخلی سرور'})
