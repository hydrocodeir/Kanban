from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "کانبان فارسی"
    env: str = "dev"
    secret_key: str = "change-me"

    database_url: str
    redis_url: str

    default_user_email: str = "demo@example.com"
    default_user_name: str = "کاربر نمونه"

    redis_board_ttl_seconds: int = 60

    auto_init_db: bool = False


settings = Settings()
