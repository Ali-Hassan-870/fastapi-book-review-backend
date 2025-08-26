from fastapi import APIRouter, Depends, status
from fastapi.exceptions import HTTPException
from src.reviews.service import ReviewService
from src.reviews.schemas import ReviewCreateModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.auth.dependencies import RoleChecker, get_current_user
from src.db.models import User

review_service = ReviewService()
review_router = APIRouter()
admin_role_checker = Depends(RoleChecker(["admin"]))
user_role_checker = Depends(RoleChecker(["admin", "user"]))


@review_router.get("/", dependencies=[admin_role_checker])
async def get_all_reviews(session: AsyncSession = Depends(get_session)):
    reviews = await review_service.get_all_reviews(session=session)
    return reviews


@review_router.get("/{review_uid}", dependencies=[user_role_checker])
async def get_review_by_uid(
    review_uid: str, session: AsyncSession = Depends(get_session)
):
    review = await review_service.get_review_by_uid(
        review_uid=review_uid, session=session
    )
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Review not found"
        )
    return review


@review_router.post("/book/{book_uid}", dependencies=[user_role_checker])
async def add_review(
    book_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    new_review = await review_service.add_review(
        user_email=current_user.email,
        book_uid=book_uid,
        review_data=review_data,
        session=session,
    )
    return new_review

@review_router.put(
    "/{review_uid}",
    dependencies=[user_role_checker]
)
async def update_review(
    review_uid: str,
    review_data: ReviewCreateModel,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    updated_review = await review_service.update_review(
        review_uid=review_uid,
        user_email=current_user.email,
        review_data=review_data,
        session=session,
    )
    return updated_review

@review_router.delete(
    "/{review_uid}",
    dependencies=[user_role_checker],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_review(
    review_uid: str,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    await review_service.delete_review(
        review_uid=review_uid,
        user_email=current_user.email,
        session=session,
    )
    return None
