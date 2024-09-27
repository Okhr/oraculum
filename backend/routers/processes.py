import math
from backend.models.book_parts import BookPart
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from typing import Annotated
from backend.models.users import User
from backend.schemas.processes import BookProcessResponseSchema
from backend.schemas.users import UserResponseSchema
from task_queue.knowledge_base_building import build_knowledge_base
from backend.routers import auth
from backend.models.books import Book
from backend.database import get_db
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from fastapi import APIRouter


router = APIRouter()


def estimate_cost(db: Session, book_id: uuid.UUID):
    story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True).all()
    # 1 token = 0.75 words, 2 times the number of tokens for question and answer, cost per 1M tokens is $0.20
    # 1$ = 100 coins
    estimated_cost = math.ceil(sum(len(part.content.split(" ")) for part in story_parts) * (1/0.75) / 1e6 * 2 * 0.2 * 100)
    return estimated_cost


@router.post("/trigger_extraction/{book_id}")
async def trigger_extraction(book_id: uuid.UUID, current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book does not belong to the current user")

    if not book.is_parsed:
        raise HTTPException(status_code=400, detail="Book has not been parsed yet")

    estimated_cost = estimate_cost(db, book_id)

    user = db.query(User).filter(User.id == current_user.id).first()
    if user.balance < estimated_cost:
        raise HTTPException(status_code=400, detail="Insufficient balance for entity extraction")

    book.extraction_start_time = datetime.now(timezone.utc)
    db.commit()

    build_knowledge_base.send(book_id=str(book_id))
    user.balance -= estimated_cost
    db.commit()


@router.get("/entity_extraction/{book_id}")
async def get_entity_extraction_process(book_id: uuid.UUID, current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)):
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book does not belong to the current user")

    estimated_cost = estimate_cost(db, book_id)

    if book.extraction_start_time is None:
        return BookProcessResponseSchema(book_id=book_id, is_requested=False, estimated_cost=estimated_cost, requested_at=None, completeness=None)

    story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True)
    extracted_story_parts = db.query(BookPart).filter(BookPart.book_id == book_id, BookPart.is_story_part == True, BookPart.is_entity_extracted == True)
    story_parts_total_length = sum([len(part.content) for part in story_parts])
    extracted_story_parts_total_length = sum([len(part.content) for part in extracted_story_parts])

    completeness = extracted_story_parts_total_length / story_parts_total_length if story_parts_total_length > 0 else 0

    return BookProcessResponseSchema(book_id=book_id, is_requested=True, estimated_cost=estimated_cost, requested_at=book.extraction_start_time, completeness=completeness)
