from itsdangerous import BadSignature, URLSafeSerializer

from app.core.config import settings

_serializer = URLSafeSerializer(settings.secret_key, salt='kanban-csrf')


def create_csrf_token(session_id: str) -> str:
    return _serializer.dumps({'sid': session_id})


def verify_csrf_token(token: str, session_id: str) -> bool:
    try:
        data = _serializer.loads(token)
    except BadSignature:
        return False
    return data.get('sid') == session_id
