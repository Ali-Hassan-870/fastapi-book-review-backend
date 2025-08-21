from passlib.context import CryptContext
from datetime import timedelta, datetime
from src.config import Config
import jwt
import uuid
import logging

password_context = CryptContext(schemes=["bcrypt"])

def generate_password_hash(password: str) -> str:
    return password_context.hash(password)

def verify_password(password: str, hash: str) -> bool:
    return password_context.verify(password, hash)

def create_jwt_token(user_data: dict, expiry: timedelta = None, refresh: bool = False) -> str:
    payload = {
        "user": user_data,
        "exp": datetime.now() + (expiry if expiry is not None else timedelta(minutes=60)),
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
        token_data = jwt.decode(
        jwt=token,
        key=Config.JWT_SECRET,
        algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWKError as jte:
        logging.exception(jte)
        return None
    except Exception as e:
        logging.exception(e)
        return None
