from fastapi import APIRouter, Depends, status
from src.auth.service import UserService
from src.auth.schemas import (
    UserSignupModel,
    UserLoginModel,
    UserBooksModel,
    EmailModel,
    PasswordResetRequestModel,
    PasswordResetConfirmModel,
)
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.utils import (
    verify_password,
    create_jwt_token,
    generate_email_token,
    verify_email_token,
    generate_password_hash,
)
from datetime import timedelta, datetime
from fastapi.responses import JSONResponse
from src.auth.dependencies import (
    RefreshTokenBearer,
    AccessTokenBearer,
    get_current_user,
    RoleChecker,
)
from src.db.redis import add_token_to_blocklist
from src.errors import (
    UserAlreadyExistsError,
    InvalidCredentialsError,
    ExpiredTokenError,
    UserNotFoundError,
)
from src.mail import create_message, mail
from src.config import Config

REFRESH_TOKEN_EXPIRY = 2

auth_router = APIRouter()
user_service = UserService()
refresh_token_bearer = RefreshTokenBearer()
access_token_bearer = AccessTokenBearer()
role_checker = RoleChecker(["admin", "user"])


@auth_router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserSignupModel, session: AsyncSession = Depends(get_session)
):
    user_email = user_data.email
    is_user_exist = await user_service.is_user_exist(user_email, session)

    if is_user_exist:
        raise UserAlreadyExistsError()

    new_user = await user_service.create_user(user_data, session)
    email_token = generate_email_token({"email": user_email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/verify/{email_token}"

    message = create_message(
        recipients=[user_email],
        subject="Verify your email",
        context={"link": link},
    )
    await mail.send_message(message, template_name="verify_email.html")
    return {
        "message": "Account Created! Check email to verify your account",
        "user": new_user,
    }


@auth_router.get("/verify/{token}")
async def verify_user_account(token: str, session: AsyncSession = Depends(get_session)):
    token_data = verify_email_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFoundError()

        await user_service.update_user(user, {"is_verified": True}, session)
        return JSONResponse(
            content={"message": "Account verified successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during verification"},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@auth_router.post("/login")
async def login(
    user_data: UserLoginModel, session: AsyncSession = Depends(get_session)
):
    email = user_data.email
    password = user_data.password

    user = await user_service.get_user_by_email(email, session)

    if user is not None:
        is_valid_password = verify_password(password, user.password_hash)

        if is_valid_password:
            access_token = create_jwt_token(
                user_data={
                    "email": user.email,
                    "user_uid": str(user.uid),
                    "role": user.role,
                }
            )

            refresh_token = create_jwt_token(
                user_data={"email": user.email, "user_uid": str(user.uid)},
                expiry=timedelta(days=REFRESH_TOKEN_EXPIRY),
                refresh=True,
            )

            return JSONResponse(
                content={
                    "message": "Login successful",
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                    "user": {"email": user.email, "uid": str(user.uid)},
                }
            )

    raise InvalidCredentialsError()


@auth_router.get("/refresh-token")
async def get_new_access_token(token_details: dict = Depends(refresh_token_bearer)):
    expiry_time = token_details["exp"]

    if datetime.fromtimestamp(expiry_time) > datetime.now():
        new_access_token = create_jwt_token(token_details["user"])
        return JSONResponse(content={"access_token": new_access_token})
    raise ExpiredTokenError()


@auth_router.get("/me", response_model=UserBooksModel)
async def get_current_user(
    user=Depends(get_current_user), _: bool = Depends(role_checker)
):
    return user


@auth_router.get("/logout")
async def logout(token_details: dict = Depends(access_token_bearer)):
    jti = token_details["jti"]
    await add_token_to_blocklist(jti)
    return JSONResponse(
        content={"message": "Logged out successfully"}, status_code=status.HTTP_200_OK
    )


@auth_router.post("/send-mail")
async def send_mail(emails: EmailModel):
    receiver_addresses = emails.addresses
    message = create_message(
        recipients=receiver_addresses,
        subject="Welcome to our app",
        context={"app_name": "Bookly"},
    )
    await mail.send_message(message, template_name="welcome_email.html")
    return {"message": "Email sent successfully"}


@auth_router.post("/password-reset-request")
async def password_reset_request(email_data: PasswordResetRequestModel):
    user_email = email_data.email
    email_token = generate_email_token({"email": user_email})
    link = f"http://{Config.DOMAIN}/api/v1/auth/password-reset-confirm/{email_token}"

    message = create_message(
        recipients=[user_email],
        subject="Reset your Account Password",
        context={"link": link},
    )
    await mail.send_message(message, template_name="reset_password.html")
    return JSONResponse(
        content={
            "message": "Please check your email for instructions to reset your password",
        },
        status_code=status.HTTP_200_OK,
    )


@auth_router.post("/password-reset-confirm/{token}")
async def reset_account_password(
    token: str,
    password: PasswordResetConfirmModel,
    session: AsyncSession = Depends(get_session),
):
    new_password = password.new_password
    token_data = verify_email_token(token)
    user_email = token_data.get("email")

    if user_email:
        user = await user_service.get_user_by_email(user_email, session)

        if not user:
            raise UserNotFoundError()

        password_hash = generate_password_hash(new_password)
        await user_service.update_user(user, {"password_hash": password_hash}, session)

        return JSONResponse(
            content={"message": "Password reset Successfully"},
            status_code=status.HTTP_200_OK,
        )

    return JSONResponse(
        content={"message": "Error occured during password reset."},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )
