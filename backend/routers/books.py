import os
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from ebooklib import epub

from core.parsing import extract_book_metadata
from .. import schemas, models, hashing
from ..database import get_db
from .auth import get_current_user


router = APIRouter()


@router.post("/upload/")
async def create_upload_file(uploaded_file: UploadFile, current_user: Annotated[schemas.UserResponseSchema, Depends(get_current_user)]):

    if uploaded_file.content_type != 'application/epub+zip':
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f'Content type : {uploaded_file.content_type} is not supported')

    if not os.path.exists(f'data/tmp'):
        os.makedirs(f'data/tmp')

    with open(f'data/tmp/{uploaded_file.filename}', 'wb') as f:
        f.write(uploaded_file.file.read())

    book = epub.read_epub(f'data/tmp/{uploaded_file.filename}')
    book_metadata = extract_book_metadata(book)
    print(book_metadata)

    if not os.path.exists(f'data/uploads/{current_user.name}'):
        os.makedirs(f'data/uploads/{current_user.name}')

    with open(f'data/uploads/{current_user.name}/{book_metadata["title"]}, {book_metadata["creator"]}.epub', 'wb') as f:
        f.write(uploaded_file.file.read())

    return {
        'filename': uploaded_file.filename,
        'user': current_user.name
    }
