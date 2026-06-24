from datetime import datetime, timedelta, timezone

from jose import jwt, JWTError

from app.core.config import settings
from app.schemas.token import TokenPayload


def create_access_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)

    payload = {
        "subject": user_id,
        "exp": expire,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> TokenPayload:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return TokenPayload(subject=payload["subject"])
    except JWTError:
        raise ValueError("Invalid token")
