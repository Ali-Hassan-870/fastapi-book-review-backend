from fastapi import FastAPI
from src.books.routes import book_router
from src.auth.routes import auth_router
from src.tags.routes import tag_router
from src.reviews.routes import review_router
from src.errors import register_error_handlers
from src.middlewares import register_middlewares

version = "v1"

app = FastAPI(
    title="Bookly",
    description="A REST API for books.",
    version=version,
)

register_error_handlers(app=app)
register_middlewares(app=app)

app.include_router(book_router, prefix=f"/api/{version}/books", tags=["books"])
app.include_router(auth_router, prefix=f"/api/{version}/auth", tags=["auth"])
app.include_router(review_router, prefix=f"/api/{version}/reviews", tags=["reviews"])
app.include_router(tag_router, prefix=f"/api/{version}/tags", tags=["tags"])
