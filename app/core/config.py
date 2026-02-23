from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    app_name: str = 'سامانه کانبان سازمانی'
    secret_key: str = Field(default='change-me-in-production')
    algorithm: str = 'HS256'
    access_token_expire_minutes: int = 60 * 8

    database_url: str = Field(
        default='mysql+pymysql://kanban:kanban@mysql:3306/kanban?charset=utf8mb4'
    )

    telegram_bot_token: str = ''
    rate_limit_window_seconds: int = 60
    max_login_attempts_per_window: int = 8


settings = Settings()
