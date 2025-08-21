from sqlmodel import SQLModel, Field, Column, Relationship
from datetime import datetime, date
import sqlalchemy.dialects.postgresql as pg
import uuid
from typing import Optional, List


class User(SQLModel, table=True):
    __tablename__ = "users"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    username: str
    email: str
    first_name: str
    last_name: str
    role: str = Field(
        sa_column=Column(pg.VARCHAR, nullable=False, server_default="user")
    )
    is_verified: bool = Field(default=False)
    password_hash: str = Field(exclude=True)
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    books: List["Book"] = Relationship(  
        back_populates="user", sa_relationship_kwargs={"lazy": "selectin"}
    )

    def __repr__(self):
        return f"<Book {self.username}>"

class Book(SQLModel, table=True):
    __tablename__ = "books"

    uid: uuid.UUID = Field(
        sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
    )
    title: str
    author: str
    publisher: str
    published_date: date
    page_count: int
    genre: str
    price: float
    user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
    created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
    user: Optional[User] = Relationship(back_populates="books") 

    def __repr__(self):
        return f"<Book {self.title}>"
    
    
# class Review(SQLModel, table=True):
#     __tablename__ = "reviews"

#     uid: uuid.UUID = Field(
#         sa_column=Column(pg.UUID, nullable=False, primary_key=True, default=uuid.uuid4)
#     )
#     rating: int = Field(ge=1, le=5)
#     review_text: str = Field(sa_column=Column(pg.VARCHAR, nullable=False))
#     user_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="users.uid")
#     book_uid: Optional[uuid.UUID] = Field(default=None, foreign_key="books.uid")
#     created_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
#     updated_at: datetime = Field(sa_column=Column(pg.TIMESTAMP, default=datetime.now))
#     user: Optional[User] = Relationship(back_populates="reviews")
#     book: Optional[Book] = Relationship(back_populates="reviews")

#     def __repr__(self):
#         return f"<Review for book {self.book_uid} by user {self.user_uid}>"
