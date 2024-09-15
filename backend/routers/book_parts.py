from backend.schemas.book_parts import TocBookPartResponseSchema
from fastapi import HTTPException
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.database import get_db
from backend.models.book_parts import BookPart
from collections import defaultdict
from typing import List, Dict
from backend.models.book_parts import BookPart

router = APIRouter()


@router.get("/toc/{book_id}")
async def get_table_of_content(book_id: str, db: Session = Depends(get_db)) -> List[TocBookPartResponseSchema]:
    book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).order_by(BookPart.sibling_index).all()
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
