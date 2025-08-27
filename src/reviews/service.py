from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.schemas import ReviewCreateModel
from src.books.service import BookService
from src.auth.service import UserService
from src.db.models import Review
from sqlmodel import select, desc
from src.errors import (
    BookNotFoundError,
    ReviewNotFoundError,
    ReviewPermissionError,
    UserNotFoundError,
)

book_service = BookService()
user_service = UserService()


class ReviewService:
    async def get_all_reviews(self, session: AsyncSession):
        statement = select(Review).order_by(desc(Review.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_review_by_uid(self, review_uid: str, session: AsyncSession):
        statement = select(Review).where(Review.uid == review_uid)
        result = await session.exec(statement)
        return result.first()

    async def add_review(
        self,
        user_email: str,
        book_uid: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        book = await book_service.get_book_by_uid(book_uid=book_uid, session=session)
        if not book:
            raise BookNotFoundError()

        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFoundError()

        review_data_dic = review_data.model_dump()
        new_review = Review(**review_data_dic, book=book, user=user)
        session.add(new_review)
        await session.commit()
        return new_review

    async def update_review(
        self,
        review_uid: str,
        user_email: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFoundError()

        review = await self.get_review_by_uid(review_uid=review_uid, session=session)
        if not review:
            raise ReviewNotFoundError()

        if review.user_uid != user.uid:
            raise ReviewPermissionError()

        update_data = review_data.model_dump()
        for k, v in update_data.items():
            setattr(review, k, v)

        await session.commit()
        await session.refresh(review)
        return review

    async def delete_review(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise UserNotFoundError()

        review = await self.get_review_by_uid(review_uid=review_uid, session=session)
        if not review:
            raise ReviewNotFoundError()

        if review.user_uid != user.uid:
            raise ReviewPermissionError()

        await session.delete(review)
        await session.commit()
