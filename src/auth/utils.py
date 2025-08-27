from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from src.config import Config
import jwt
import uuid
from src.errors import InvalidTokenError, ExpiredTokenError, JWTDecodeError

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
        raise ExpiredTokenError()
    except jwt.InvalidTokenError:
        raise InvalidTokenError()
    except Exception:
        raise JWTDecodeError()
