from datetime import datetime, timedelta
import jwt
from django.conf import settings


def create_token(user_id: int) -> dict:
    """Создание токена для пользователя (время жизни и шифрование в настройках)"""

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    return {
        "user_id": user_id,
        "access_token": create_access_token(
            data={"user_id": user_id}, expires_delta=access_token_expires
        ),
        "token_type": "Token",
    }


def create_access_token(data: dict, expires_delta: timedelta = None):
    """Создание access токена"""
    DEFAULT_DELTA_EXPIRES = 15  # 15 минут по умолчанию
    to_encode = data.copy()
    if expires_delta is not None:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=DEFAULT_DELTA_EXPIRES)
    to_encode.update({"exp": expire, "sub": "access"})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt
