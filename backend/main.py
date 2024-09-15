from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import auth, users, books, book_parts

app = FastAPI()

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')
app.include_router(users.router, tags=['Users'], prefix='/api/users')
app.include_router(books.router, tags=['Books'], prefix='/api/books')
app.include_router(book_parts.router, tags=['Book Parts'], prefix='/api/bookparts')
