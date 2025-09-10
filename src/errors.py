from typing import Any, Callable
from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse


class BooklyError(Exception):
    """Base class for all Bookly application errors."""


class InvalidTokenError(BooklyError):
    """User has provided an invalid or expired token."""


class RevokedTokenError(BooklyError):
    """User has provided a token that has been revoked."""


class AccessTokenRequiredError(BooklyError):
    """User has provided a refresh token when an access token is required."""


class RefreshTokenRequiredError(BooklyError):
    """User has provided an access token when a refresh token is required."""


class PermissionDeniedError(BooklyError):
    """User does not have the required role to perform this operation."""


class UserAlreadyExistsError(BooklyError):
    """A user with this email already exists during signup."""


class InvalidCredentialsError(BooklyError):
    """User has provided an invalid email or password during login."""


class ExpiredTokenError(BooklyError):
    """The provided JWT token has expired."""


class JWTDecodeError(BooklyError):
    """Failed to decode the JWT token due to invalid format or signature."""


class UserNotFoundError(BooklyError):
    """Raised when a user cannot be found in the system."""


class UserNotVerifiedError(BooklyError):
    """Raised when a user has not verified their email."""


class BookNotFoundError(BooklyError):
    """Raised when a book with the given identifier does not exist."""


class ReviewNotFoundError(BooklyError):
    """Raised when a review with the given identifier does not exist."""


class ReviewPermissionError(BooklyError):
    """Raised when a user attempts to modify or delete a review they do not own."""


class TagNotFoundError(BooklyError):
    """Raised when a tag with the given identifier does not exist."""


class TagAlreadyExistsError(BooklyError):
    """Raised when trying to create a tag that already exists."""


def create_exception_handler(
    status_code: int, initial_detail: Any
) -> Callable[[Request, Exception], JSONResponse]:
    async def exception_handler(request: Request, exc: BooklyError):
        return JSONResponse(content=initial_detail, status_code=status_code)

    return exception_handler


def register_error_handlers(app: FastAPI):
    """Register all custom exception handlers for the Bookly application."""

    # User-related exceptions
    app.add_exception_handler(
        UserAlreadyExistsError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "A user with this email address already exists",
                "error_code": "user_already_exists",
                "resolution": "Please use a different email address or try logging in",
            },
        ),
    )

    app.add_exception_handler(
        UserNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "The requested user could not be found",
                "error_code": "user_not_found",
                "resolution": "Please verify the user identifier and try again",
            },
        ),
    )

    app.add_exception_handler(
        UserNotVerifiedError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "Your account is not verified. Please verify your email before logging in.",
                "error_code": "user_not_verified",
                "resolution": "Check your email inbox or spam folder for the verification link.",
            },
        ),
    )

    app.add_exception_handler(
        InvalidCredentialsError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "The provided email or password is incorrect",
                "error_code": "invalid_credentials",
                "resolution": "Please check your credentials and try again",
            },
        ),
    )

    # Token-related exceptions
    app.add_exception_handler(
        InvalidTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "The provided token is invalid or has expired",
                "error_code": "invalid_token",
                "resolution": "Please authenticate again to obtain a new token",
            },
        ),
    )

    app.add_exception_handler(
        RevokedTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "The provided token has been revoked and is no longer valid",
                "error_code": "token_revoked",
                "resolution": "Please authenticate again to obtain a new token",
            },
        ),
    )

    app.add_exception_handler(
        ExpiredTokenError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "The provided token has expired",
                "error_code": "token_expired",
                "resolution": "Please authenticate again to obtain a new token",
            },
        ),
    )

    app.add_exception_handler(
        AccessTokenRequiredError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "This operation requires a valid access token",
                "error_code": "access_token_required",
                "resolution": "Please provide a valid access token in the Authorization header",
            },
        ),
    )

    app.add_exception_handler(
        RefreshTokenRequiredError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "This operation requires a valid refresh token",
                "error_code": "refresh_token_required",
                "resolution": "Please provide a valid refresh token",
            },
        ),
    )

    app.add_exception_handler(
        JWTDecodeError,
        create_exception_handler(
            status_code=status.HTTP_401_UNAUTHORIZED,
            initial_detail={
                "message": "Unable to process the provided token due to invalid format",
                "error_code": "jwt_decode_error",
                "resolution": "Please ensure you are providing a valid JWT token",
            },
        ),
    )

    # Permission-related exceptions
    app.add_exception_handler(
        PermissionDeniedError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You do not have sufficient permissions to perform this action",
                "error_code": "permission_denied",
                "resolution": "Please contact an administrator if you believe this is an error",
            },
        ),
    )

    # Book-related exceptions
    app.add_exception_handler(
        BookNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "The requested book could not be found",
                "error_code": "book_not_found",
                "resolution": "Please verify the book identifier and try again",
            },
        ),
    )

    # Review-related exceptions
    app.add_exception_handler(
        ReviewNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "The requested review could not be found",
                "error_code": "review_not_found",
                "resolution": "Please verify the review identifier and try again",
            },
        ),
    )

    app.add_exception_handler(
        ReviewPermissionError,
        create_exception_handler(
            status_code=status.HTTP_403_FORBIDDEN,
            initial_detail={
                "message": "You do not have permission to modify or delete this review",
                "error_code": "review_permission_denied",
                "resolution": "You can only modify or delete reviews that you have created",
            },
        ),
    )

    # Tag-related exceptions
    app.add_exception_handler(
        TagNotFoundError,
        create_exception_handler(
            status_code=status.HTTP_404_NOT_FOUND,
            initial_detail={
                "message": "The requested tag could not be found",
                "error_code": "tag_not_found",
                "resolution": "Please verify the tag identifier and try again",
            },
        ),
    )

    app.add_exception_handler(
        TagAlreadyExistsError,
        create_exception_handler(
            status_code=status.HTTP_409_CONFLICT,
            initial_detail={
                "message": "A tag with this name already exists",
                "error_code": "tag_already_exists",
                "resolution": "Please choose a different tag name or use the existing tag",
            },
        ),
    )

    # Generic server error handler
    @app.exception_handler(500)
    async def internal_server_error_handler(request, exc):
        """Handle internal server errors with a user-friendly message."""
        return JSONResponse(
            content={
                "message": "An unexpected error occurred while processing your request",
                "error_code": "internal_server_error",
                "resolution": "Please try again later or contact support if the problem persists",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Generic BooklyError handler for any unhandled custom exceptions
    @app.exception_handler(BooklyError)
    async def bookly_error_handler(request, exc):
        """Handle any unregistered BooklyError exceptions."""
        return JSONResponse(
            content={
                "message": "An application error occurred",
                "error_code": "bookly_error",
                "details": str(exc),
                "resolution": "Please contact support if this error persists",
            },
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )