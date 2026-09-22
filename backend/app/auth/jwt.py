import datetime
from typing import Dict, Any, Optional
import jwt
from fastapi import HTTPException, status
from app.config.settings import settings


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[datetime.timedelta] = None
) -> str:
    """
    Creates a signed JSON Web Token with expiration timestamp and user claims.
    """
    to_encode = data.copy()
    now = datetime.datetime.now(datetime.timezone.utc)

    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + datetime.timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({
        "exp": expire,
        "iat": now
    })

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JSON Web Token signature and expiration.
    Raises HTTPException 401 if expired, invalid, or malformed.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except (jwt.InvalidTokenError, jwt.PyJWTError):
        raise credentials_exception
