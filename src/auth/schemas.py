from pydantic import BaseModel, Field
from datetime import datetime
import uuid
from typing import List
from src.books.schemas import BookModel
from src.reviews.schemas import ReviewModel


class UserModel(BaseModel):
    uid: uuid.UUID
    username: str
    email: str
    first_name: str
    last_name: str
    is_verified: bool
    created_at: datetime
    updated_at: datetime


class UserSignupModel(BaseModel):
    first_name: str = Field(min_length=2, max_length=50)
    last_name: str = Field(min_length=2, max_length=50)
    username: str = Field(min_length=3, max_length=30)
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)


class UserLoginModel(BaseModel):
    email: str = Field(max_length=254)
    password: str = Field(min_length=8, max_length=128)


class UserBooksModel(UserModel):
    books: List[BookModel]
    reviews: List[ReviewModel]


class EmailModel(BaseModel):
    addresses: List[str]


class PasswordResetRequestModel(BaseModel):
    email: str


class PasswordResetConfirmModel(BaseModel):
    new_password: str
