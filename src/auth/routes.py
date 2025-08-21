from fastapi import APIRouter, Depends, status
from src.auth.service import UserService
from src.auth.schemas import UserSignupModel, UserModel, UserLoginModel, UserBooksModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from fastapi.exceptions import HTTPException
from src.auth.utils import verify_password, create_jwt_token
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from src.auth.dependencies import RefreshTokenBearer, AccessTokenBearer, get_current_user, RoleChecker
from src.db.redis import add_token_to_blocklist

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])

@auth_router.post("/signup", response_model=UserModel, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserSignupModel, session: AsyncSession = Depends(get_session)):
    user_email = user_data.email
    is_user_exist = await user_service.is_user_exist(user_email, session)

    if is_user_exist:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User with this email already exist")
    
    new_user = await user_service.create_user(user_data, session)
    return new_user

@auth_router.post("/login")
async def login(user_data: UserLoginModel, session: AsyncSession = Depends(get_session)):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        is_valid_password = verify_password(password, user.password_hash)

        if is_valid_password:
            access_token = create_jwt_token(
                user_data={"email": user.email, "user_uid": str(user.uid), "role": user.role}
            )
            
            refresh_token = create_jwt_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )
    
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid email and password")

@auth_router.get("/refresh-token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry_time = token_details["exp"]

    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_jwt_token(token_details["user"])
        return JSONResponse(
            content={"access_token": new_access_token}
        )
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Or expired token"
    )

@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(user = Depends(get_current_user), _: bool = Depends(role_checker)):
    return user

@auth_router.get("/logout")
async def logout(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]
    await add_token_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully"},
        status_code=status.HTTP_200_OK
    )