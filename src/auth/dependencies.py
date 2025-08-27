from fastapi.security import HTTPBearer
from fastapi import Request, Depends
from src.auth.utils import decode_jwt_token
from src.db.redis import is_token_in_blocklist
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.service import UserService
from typing import List
from src.db.models import User
from src.errors import (
    RevokedTokenError,
    AccessTokenRequiredError,
    RefreshTokenRequiredError,
    PermissionDeniedError,
)

user_service = UserService()


class TokenBearer(HTTPBearer):
    def __init__(self, auto_error=True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        cred = await super().__call__(request)
        token = cred.credentials
        token_data = decode_jwt_token(token)

        if await is_token_in_blocklist(token_data["jti"]):
            raise RevokedTokenError()

        self.verify_token(token_data)
        return token_data

    def verify_token(self, token_data):
        raise NotImplementedError("Please override this method in child classes")


class AccessTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if token_data and token_data["refresh"]:
            raise AccessTokenRequiredError()


class RefreshTokenBearer(TokenBearer):
    def verify_token(self, token_data: dict) -> None:
        if token_data and not token_data["refresh"]:
            raise RefreshTokenRequiredError()


async def get_current_user(
    token_details: dict = Depends(AccessTokenBearer()),
    session: AsyncSession = Depends(get_session),
):
    email = token_details["user"]["email"]
    user = await user_service.get_user_by_email(email, session)
    return user


class RoleChecker:
    def __init__(self, permitted_roles: List[str]) -> None:
        self.permitted_roles = permitted_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> any:
        if current_user.role in self.permitted_roles:
            return True

        raise PermissionDeniedError()
