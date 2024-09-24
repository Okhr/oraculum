import uuid
from backend.models.books import Book
from backend.routers import auth
from backend.schemas.book_parts import BookPartUpdateSchema, BookPartResponseSchema
from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.book_parts import BookPart
from typing import Annotated, List
from backend.models.book_parts import BookPart
from backend.schemas.users import UserResponseSchema

router = APIRouter()


@router.get("/book_part_id/{book_part_id}")
async def get_book_part(
        book_part_id: str,
        current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)],
        db: Session = Depends(get_db)) -> BookPartResponseSchema:

    book_part = db.query(BookPart).filter(BookPart.id == book_part_id).first()
    book = db.query(Book).filter(Book.id == book_part.book_id).first()

    if (not book) or (not book_part):
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book part does not belong to the current user")

    return BookPartResponseSchema(
        id=book_part.id,
        book_id=book_part.book_id,
        parent_id=book_part.parent_id,
        label=book_part.label,
        content=book_part.content,
        sibling_index=book_part.sibling_index,
        is_story_part=book_part.is_story_part,
        is_entity_extracted=book_part.is_entity_extracted,
        created_at=book_part.created_at
    )


@router.get("/book_id/{book_id}")
async def get_book_parts(
        book_id: str,
        current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)],
        db: Session = Depends(get_db)) -> List[BookPartResponseSchema]:

    book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()
    book = db.query(Book).filter(Book.id == book_id).first()
    if (not book) or (not book_parts):
        raise HTTPException(status_code=404, detail="Book parts not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book parts do not belong to the current user")


@router.put("/update/{book_part_id}")
async def update_book_part(
    book_part_id: uuid.UUID,
    book_part_update: BookPartUpdateSchema,
    current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)],
    db: Session = Depends(get_db)
) -> BookPartResponseSchema:

    book_part = db.query(BookPart).filter(BookPart.id == book_part_id).first()
    if not book_part:
        raise HTTPException(status_code=404, detail="Book part not found")

    book = db.query(Book).filter(Book.id == book_part.book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book part does not belong to the current user")

    book_part.is_story_part = book_part_update.is_story_part
    db.commit()
    db.refresh(book_part)

    return BookPartResponseSchema(
        id=book_part.id,
        book_id=book_part.book_id,
        parent_id=book_part.parent_id,
        label=book_part.label,
        content=book_part.content,
        sibling_index=book_part.sibling_index,
        is_story_part=book_part.is_story_part,
        is_entity_extracted=book_part.is_entity_extracted,
        created_at=book_part.created_at
    )
