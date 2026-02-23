import httpx
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.entities import User


async def send_telegram_message(chat_id: str, text: str) -> None:
    if not settings.telegram_bot_token or not chat_id:
        return
    url = f'https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage'
    async with httpx.AsyncClient(timeout=8.0) as client:
        await client.post(url, json={'chat_id': chat_id, 'text': text})


async def notify_user(db: Session, user_id: int, text: str) -> None:
    user = db.get(User, user_id)
    if not user or not user.notify_enabled or not user.telegram_chat_id:
        return
    await send_telegram_message(user.telegram_chat_id, text)
