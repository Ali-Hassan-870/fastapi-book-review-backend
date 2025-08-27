from fastapi import status
from fastapi.exceptions import HTTPException
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select, desc
from src.db.models import Tag
from src.tags.schemas import TagCreateModel, TagAddModel
from src.books.service import BookService

book_service = BookService()


class TagService:
    async def get_all_tags(self, session: AsyncSession):
        statement = select(Tag).order_by(desc(Tag.created_at))
        result = await session.exec(statement)
        return result.all()

    async def get_tag_by_uid(self, tag_uid: str, session: AsyncSession):
        statement = select(Tag).where(Tag.uid == tag_uid)
        result = await session.exec(statement)
        return result.first()

    async def add_tag(self, tag_data: TagCreateModel, session: AsyncSession):
        statement = select(Tag).where(Tag.name == tag_data.name)
        result = await session.exec(statement)
        tag = result.first()
        if tag:
            raise HTTPException(
                detail="Tag already exist", status_code=status.HTTP_403_FORBIDDEN
            )

        new_tag = Tag(name=tag_data.name)
        session.add(new_tag)
        await session.commit()
        await session.refresh(new_tag)
        return new_tag

    async def update_tag(
        self, tag_uid: str, tag_data: TagCreateModel, session: AsyncSession
    ):
        tag = await self.get_tag_by_uid(tag_uid=tag_uid, session=session)
        if not tag:
            raise HTTPException(
                detail="Tag not found", status_code=status.HTTP_404_NOT_FOUND
            )

        updated_data_dic = tag_data.model_dump()
        for k, v in updated_data_dic.items():
            setattr(tag, k, v)

        await session.commit()
        await session.refresh(tag)
        return tag

    async def delete_tag(self, tag_uid: str, session: AsyncSession):
        tag = await self.get_tag_by_uid(tag_uid=tag_uid, session=session)
        if not tag:
            raise HTTPException(
                detail="Tag not found", status_code=status.HTTP_404_NOT_FOUND
            )

        await session.delete(tag)
        await session.commit()

    async def add_tags_to_book(
        self, book_uid: str, tags_data: TagAddModel, session: AsyncSession
    ):
        book = await book_service.get_book_by_uid(book_uid=book_uid, session=session)
        if not book:
            raise HTTPException(
                detail="Book not found", status_code=status.HTTP_404_NOT_FOUND
            )
        
        for tag_item in tags_data.tags:
            result = await session.exec(select(Tag).where(Tag.name == tag_item.name))
            tag = result.one_or_none()
            if not tag:
                tag = Tag(name=tag_item.name)
            
            book.tags.append(tag)
        
        session.add(book)
        await session.commit()
        await session.refresh(book)
        return book
