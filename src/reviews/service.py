from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from src.reviews.schemas import ReviewCreateModel
from src.books.service import BookService
from src.auth.service import UserService
from src.db.models import Review
import logging
from sqlmodel import select, desc

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
        try:
            book = await book_service.get_book_by_uid(
                book_uid=book_uid, session=session
            )
            if not book:
                raise HTTPException(
                    detail="book not found", status_code=status.HTTP_404_NOT_FOUND
                )

            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )
            if not user:
                raise HTTPException(
                    detail="user not found", status_code=status.HTTP_404_NOT_FOUND
                )

            review_data_dic = review_data.model_dump()
            new_review = Review(**review_data_dic, book=book, user=user)
            session.add(new_review)
            await session.commit()
            return new_review
        
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                detail="something went wrong",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def update_review(
        self,
        review_uid: str,
        user_email: str,
        review_data: ReviewCreateModel,
        session: AsyncSession,
    ):
        try:
            user = await user_service.get_user_by_email(
                email=user_email, session=session
            )
            if not user:
                raise HTTPException(
                    detail="user not found", status_code=status.HTTP_404_NOT_FOUND
                )

            review = await self.get_review_by_uid(
                review_uid=review_uid, session=session
            )
            if not review:
                raise HTTPException(
                    detail="review not found", status_code=status.HTTP_404_NOT_FOUND
                )

            if review.user_uid != user.uid:
                raise HTTPException(
                    status_code=403, detail="you cannot update this review"
                )

            review.rating = review_data.rating
            review.review_text = review_data.review_text
            session.add(review)
            await session.commit()
            await session.refresh(review)
            return review
        
        except HTTPException:
            raise
        except Exception as e:
            logging.exception(e)
            raise HTTPException(
                detail="something went wrong",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    async def delete_review(
        self, review_uid: str, user_email: str, session: AsyncSession
    ):
        user = await user_service.get_user_by_email(email=user_email, session=session)
        if not user:
            raise HTTPException(
                detail="user not found", status_code=status.HTTP_404_NOT_FOUND
            )

        review = await self.get_review_by_uid(review_uid=review_uid, session=session)
        if not review:
            raise HTTPException(
                detail="review not found", status_code=status.HTTP_404_NOT_FOUND
            )

        if review.user_uid != user.uid:
            raise HTTPException(
                detail="cannot delete this review",
                status_code=status.HTTP_403_FORBIDDEN,
            )

        await session.delete(review)
        await session.commit()
