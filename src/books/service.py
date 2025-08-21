from sqlmodel.ext.asyncio.session import AsyncSession
from src.books.schemas import BookCreateModel, BookUpdateModel
from src.db.models import Book
from sqlmodel import select, desc
from datetime import datetime
import uuid


class BookService:
    async def get_books(self, session: AsyncSession):
        statement = select(Book).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_book_by_uid(self, book_uid: str, session: AsyncSession):
        statement = select(Book).where(Book.uid == book_uid)
        result = await session.exec(statement)
        book = result.first()
        return book if book is not None else None
    
    async def get_user_books(self, user_uid: str, session: AsyncSession):
        user_uuid = uuid.UUID(user_uid)
        
        statement = select(Book).where(Book.user_uid == user_uuid).order_by(desc(Book.created_at))
        result = await session.exec(statement)
        return result.all()

    async def create_book(self, book_date: BookCreateModel, user_uid: str, session: AsyncSession):
        book_date_dic = book_date.model_dump()
        new_book = Book(**book_date_dic)
        new_book.published_date = datetime.strptime(
            book_date_dic["published_date"], "%Y-%m-%d"
        )
        new_book.user_uid = uuid.UUID(user_uid)
        session.add(new_book)
        await session.commit()
        return new_book

    async def update_book(
        self, book_uid: str, updated_book_data: BookUpdateModel, session: AsyncSession
    ):
        book_to_update = await self.get_book_by_uid(book_uid, session)

        if book_to_update is not None:
            updated_book_data_dic = updated_book_data.model_dump()

            for key, value in updated_book_data_dic.items():
                setattr(book_to_update, key, value)

            await session.commit()
            return book_to_update
        else:
            return None

    async def delete_book(self, book_uid: str, session: AsyncSession):
        book_to_delete = await self.get_book_by_uid(book_uid, session)

        if book_to_delete is not None:
            await session.delete(book_to_delete)
            await session.commit()
            return {}
        else:
            return None
