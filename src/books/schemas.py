from pydantic import BaseModel
import uuid
from datetime import datetime, date
from typing import List
from src.reviews.schemas import ReviewModel
from src.tags.schemas import TagModel

class BookModel(BaseModel):
    uid: uuid.UUID
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    genre: str
    price: float
    created_at: datetime
    updated_at: datetime

class BookDetailModel(BookModel):
    reviews: List[ReviewModel]
    tags: List[TagModel]

class BookCreateModel(BaseModel):
    title: str
    author: str
    publisher: str
    published_date: str
    page_count: int
    genre: str
    price: float

class BookUpdateModel(BaseModel):
    title: str
    author: str
    publisher: str
    page_count: int
    genre: str
    price: float