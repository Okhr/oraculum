import hashlib
import os
from typing import Annotated
import uuid
import dotenv
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from ebooklib import epub
from sqlalchemy.orm import Session
from redis import Redis
from rq import Queue, Retry

from core.parsing import extract_book_metadata, get_cover_image_as_base64
from task_queue.parsing import extract_text_parts_task

from backend.schemas import books as book_schemas
from backend.schemas import users as user_schemas
from backend.database import get_db
from backend.routers import auth
from backend.models.books import Book, FileType
from backend.models.books import Book
from backend.models.text_parts import TextPart

dotenv.load_dotenv()

q = Queue(connection=Redis(host=os.environ.get("REDIS_HOST"), port=os.environ.get("REDIS_PORT")))

router = APIRouter()


@router.post("/upload/")
async def create_upload_file(
        uploaded_file: UploadFile,
        current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)],
        db: Session = Depends(get_db)
) -> book_schemas.BookUploadResponseSchema:

    if uploaded_file.content_type != 'application/epub+zip':
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'Content type : {uploaded_file.content_type} is not supported')

    max_file_size = 100 * 1024 * 1024
    if uploaded_file.size > max_file_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail='File size exceeds the maximum limit of 100 MB')
    try:
        book = epub.read_epub(uploaded_file.file)
        book_metadata = extract_book_metadata(book)
        cover_image_base64 = get_cover_image_as_base64(book)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f'Error processing the file: {str(e)}')

    file_data = uploaded_file.file.read()
    data_hash = hashlib.sha256(file_data).hexdigest()

    # Check if the file has been already uploaded by the user
    existing_book = db.query(Book).filter(Book.user_id == current_user.id, Book.data_hash == data_hash).first()
    if existing_book:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='File has been already uploaded by this user')

    # Create a new BookFile instance and save it to the database
    new_book_file = Book(
        user_id=current_user.id,
        file_type=FileType.epub,
        original_file_name=uploaded_file.filename,
        file_size=uploaded_file.size,
        file_data=file_data,
        author=book_metadata["creator"],
        title=book_metadata["title"],
        data_hash=data_hash,
        cover_image_base64=cover_image_base64
    )
    db.add(new_book_file)
    db.commit()
    db.refresh(new_book_file)

    # Add a task to parse and extract book text_parts
    q.enqueue(extract_text_parts_task,
              retry=Retry(max=3, interval=[60]),
              kwargs={
                  'book': book,
                  'book_id': str(new_book_file.id),
              },
              result_ttl=3.156e7,  # 1 year
              meta={
                  'user_id': str(current_user.id),
                  'book_id': str(new_book_file.id),
              })

    return book_schemas.BookUploadResponseSchema(
        id=new_book_file.id,
        user_id=current_user.id,
        author=new_book_file.author,
        title=new_book_file.title,
        upload_date=new_book_file.upload_date,
        file_type=new_book_file.file_type,
        original_file_name=new_book_file.original_file_name,
        file_size=new_book_file.file_size,
        is_parsed=new_book_file.is_parsed,
    )


@router.get("/")
async def get_books(
    current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)
) -> list[book_schemas.BookResponseSchema]:
    books = db.query(Book).filter(Book.user_id == current_user.id).all()

    return [book_schemas.BookResponseSchema(
        id=book.id,
        user_id=book.user_id,
        author=book.author,
        title=book.title,
        upload_date=book.upload_date,
        file_type=book.file_type,
        cover_image_base64=book.cover_image_base64,
        is_parsed=book.is_parsed,
    ) for book in books]


@router.delete("/delete/{book_id}")
async def delete_book(
    book_id: uuid.UUID,
    current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)
) -> book_schemas.BookResponseSchema:
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    # Delete all the text_parts associated with the book
    db.query(TextPart).filter(TextPart.book_id == book_id).delete()

    db.delete(book)
    db.commit()

    return book_schemas.BookResponseSchema(
        id=book.id,
        user_id=book.user_id,
        author=book.author,
        title=book.title,
        upload_date=book.upload_date,
        file_type=book.file_type,
        cover_image_base64=book.cover_image_base64,
        is_parsed=book.is_parsed,
    )


@router.put("/update/{book_id}")
async def update_book(
    book_id: uuid.UUID,
    book_update: book_schemas.BookUpdateSchema,
    current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)
) -> book_schemas.BookResponseSchema:
    book = db.query(Book).filter(Book.id == book_id, Book.user_id == current_user.id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book_update.author is not None:
        book.author = book_update.author
    if book_update.title is not None:
        book.title = book_update.title

    db.commit()
    db.refresh(book)

    return book_schemas.BookResponseSchema(
        id=book.id,
        user_id=book.user_id,
        author=book.author,
        title=book.title,
        upload_date=book.upload_date,
        file_type=book.file_type,
        cover_image_base64=book.cover_image_base64,
        is_parsed=book.is_parsed,
    )
