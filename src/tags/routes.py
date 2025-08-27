from typing import List
from fastapi import APIRouter, Depends, status
from src.tags.service import TagService
from src.auth.dependencies import RoleChecker
from src.tags.schemas import TagModel, TagCreateModel, TagAddModel
from sqlmodel.ext.asyncio.session import AsyncSession
from src.db.main import get_session
from src.books.schemas import BookModel

tag_router = APIRouter()
tag_service = TagService()
user_role_checker = Depends(RoleChecker(["user", "admin"]))


@tag_router.get("/", response_model=List[TagModel], dependencies=[user_role_checker])
async def get_all_tags(session: AsyncSession = Depends(get_session)):
    tags = await tag_service.get_all_tags(session=session)
    return tags


@tag_router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    dependencies=[user_role_checker],
    response_model=TagModel,
)
async def add_tag(
    tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    tag = await tag_service.add_tag(tag_data=tag_data, session=session)
    return tag


@tag_router.put("/{tag_uid}", response_model=TagModel, dependencies=[user_role_checker])
async def update_tag(
    tag_uid: str, tag_data: TagCreateModel, session: AsyncSession = Depends(get_session)
):
    updated_tag = await tag_service.update_tag(
        tag_uid=tag_uid, tag_data=tag_data, session=session
    )
    return updated_tag


@tag_router.delete(
    "/{tag_uid}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[user_role_checker],
)
async def delete_tag(tag_uid: str, session: AsyncSession = Depends(get_session)):
    await tag_service.delete_tag(tag_uid=tag_uid, session=session)


@tag_router.post(
    "/book/{book_uid}", response_model=BookModel, dependencies=[user_role_checker]
)
async def add_tags_to_book(
    book_uid: str,
    tags_data: TagAddModel,
    session: AsyncSession = Depends(get_session),
):
    book_with_tag = await tag_service.add_tags_to_book(
        book_uid=book_uid, tags_data=tags_data, session=session
    )
    return book_with_tag
