import json
from redis import Redis
from app.core.config import settings

redis_client = Redis.from_url(settings.redis_url, decode_responses=True)


def cache_get_board(project_id: int) -> dict | None:
    key = f"board:{project_id}"
    val = redis_client.get(key)
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return None


def cache_set_board(project_id: int, data: dict) -> None:
    key = f"board:{project_id}"
    redis_client.setex(key, settings.redis_board_ttl_seconds, json.dumps(data, ensure_ascii=False))


def cache_invalidate_board(project_id: int) -> None:
    key = f"board:{project_id}"
    redis_client.delete(key)
