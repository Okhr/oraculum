from fastapi import FastAPI
from .routers import auth, users, books

app = FastAPI()
app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(users.router, tags=['Users'], prefix='/api/users')
app.include_router(books.router, tags=['Books'], prefix='/api/books')
