from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from src.config import Config
from fastapi import HTTPException, status
import jwt
import uuid

password_context = CryptContext(schemes=["bcrypt"])

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_jwt_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now(timezone.utc) + (expiry if expiry else timedelta(minutes=60)),
        "jti": str(uuid.uuid4()),
        "refresh": refresh
    }

    token = jwt.encode(
        payload=payload,
        key=Config.JWT_SECRET,
        algorithm=Config.JWT_ALGORITHM
    )
    return token

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
