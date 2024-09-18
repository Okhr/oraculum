from backend.schemas.book_parts import TocBookPartResponseSchema, BookPartResponseSchema
from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.book_parts import BookPart
from typing import List
from backend.models.book_parts import BookPart

router = APIRouter()


@router.get("/toc/{book_id}")
async def get_table_of_content(book_id: str, db: Session = Depends(get_db)) -> List[TocBookPartResponseSchema]:
    book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()
    if not book_parts:
        raise HTTPException(status_code=404, detail="Book not found")

    def build_response(book_parts, parent_id=None):
        response = []
        for part in book_parts:
            if part.parent_id == parent_id:
                children = build_response(book_parts, part.id)
                response_part = TocBookPartResponseSchema(
                    id=part.id,
                    book_id=part.book_id,
                    parent_id=part.parent_id,
                    label=part.label,
                    created_at=part.created_at,
                    sibling_index=part.sibling_index,
                    is_story_part=part.is_story_part,
                    children=children
                )
                response.append(response_part)
        return response

    toc = build_response(book_parts)

    return toc


@router.get("/book_part_id/{book_part_id}")
async def get_book_part(book_part_id: str, db: Session = Depends(get_db)) -> BookPartResponseSchema:
    book_part = db.query(BookPart).filter(BookPart.id == book_part_id).first()
    if not book_part:
        raise HTTPException(status_code=404, detail="Book part not found")

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
async def get_book_parts(book_id: str, db: Session = Depends(get_db)) -> List[BookPartResponseSchema]:
    book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()
    if not book_parts:
        raise HTTPException(status_code=404, detail="Book parts not found")

    return [
        BookPartResponseSchema(
            id=part.id,
            book_id=part.book_id,
            parent_id=part.parent_id,
            label=part.label,
            content=part.content,
            sibling_index=part.sibling_index,
            is_story_part=part.is_story_part,
            is_entity_extracted=part.is_entity_extracted,
            created_at=part.created_at
        )
        for part in book_parts
    ]
