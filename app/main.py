from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.routes.api.projects import router as projects_router
from app.routes.api.columns import router as columns_router
from app.routes.api.tasks import router as tasks_router
from app.routes.web.pages import router as pages_router
from app.routes.web.htmx import router as htmx_router
from app.routes.web.auth import router as auth_router

from app.db.init_db import create_all, seed_default_user_and_sample, ensure_runtime_migrations
from app.db.session import SessionLocal


setup_logging()

app = FastAPI(title=settings.app_name, version="0.1.0")

# CORS (برای توسعه)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.add_middleware(SessionMiddleware, secret_key=settings.secret_key, same_site='lax')

app.include_router(auth_router)
app.include_router(pages_router)
app.include_router(htmx_router)

api = FastAPI(title=f"{settings.app_name} API", version="0.1.0")
api.include_router(projects_router)
api.include_router(columns_router)
api.include_router(tasks_router)

app.mount("/api/v1", api)


@app.on_event("startup")
def _startup_init_db():
    # برای داکر/نسخه مینیمال: در صورت فعال بودن، جدول‌ها ساخته و داده نمونه ایجاد می‌شود
    if getattr(settings, "auto_init_db", False):
        create_all()
        db = SessionLocal()
        try:
            ensure_runtime_migrations(db)
            seed_default_user_and_sample(db)
        finally:
            db.close()


@app.get("/health", tags=["health"])
def health():
    return {"ok": True, "app": settings.app_name}
