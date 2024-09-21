import math
from backend.models.book_parts import BookPart
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from typing import Annotated
from backend.schemas.processes import BookProcessResponseSchema
from task_queue.entity_extraction import extract_entities_task
from backend.schemas import users as user_schemas
from backend.routers import auth
from backend.models.books import Book
from backend.database import get_db
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter


router = APIRouter()


@router.post("/trigger_extraction/{book_id}")
async def trigger_extraction(book_id: uuid.UUID, current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book does not belong to the current user")

    if not book.is_parsed:
        raise HTTPException(status_code=400, detail="Book has not been parsed yet")

    if book.is_parsed:
        book.extraction_start_time = datetime.now(timezone.utc)
        db.commit()
        extract_entities_task.send(book_id=str(book_id))
    else:
        raise HTTPException(status_code=400, detail="Book has not been parsed yet")


@router.get("/entity_extraction/{book_id}")
async def get_entity_extraction_process(book_id: uuid.UUID, current_user: Annotated[user_schemas.UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book does not belong to the current user")

    story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True).all()

    # 1 token = 0.75 words, 2 times the number of tokens for question and answer, cost per 1M tokens is $0.20
    # 1$ = 1000 coins
    estimated_cost = math.ceil(sum(len(part.content.split(" ")) for part in story_parts) * (1/0.75) / 1e6 * 2 * 0.2 * 1000)

    if book.extraction_start_time is None:
        return BookProcessResponseSchema(book_id=book_id, is_requested=False, estimated_cost=estimated_cost, requested_at=None, completeness=None)

    story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True)
    extracted_story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True, BookPart.is_entity_extracted == True)
    story_parts_total_length = sum([len(part.content) for part in story_parts])
    extracted_story_parts_total_length = sum([len(part.content) for part in extracted_story_parts])

    completeness = extracted_story_parts_total_length / story_parts_total_length if story_parts_total_length > 0 else 0

    return BookProcessResponseSchema(book_id=book_id, is_requested=True, estimated_cost=estimated_cost, requested_at=book.extraction_start_time, completeness=completeness)
