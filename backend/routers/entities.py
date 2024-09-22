from backend.models.books import Book
from backend.models.kb_entries import KnowledgeBaseEntry
from sqlalchemy import func
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database import get_db
from typing import Annotated, List
from backend.routers import auth
from backend.schemas.entities import EntityResponseSchema, Fact
from backend.schemas.users import UserResponseSchema

router = APIRouter()


@router.get("/book_id/{book_id}")
async def get_book_entities(book_id: str, current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)) -> List[EntityResponseSchema]:
    kb_entries = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.book_id == book_id).all()
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not kb_entries:
        raise HTTPException(status_code=404, detail="Knowledge base entries not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The entries do not belong to the current user")

    entities = []
    for kb_entry in kb_entries:
        entity = next((e for e in entities if e.name == kb_entry.entity_name), None)
        if entity is None:
            entity = EntityResponseSchema(
                name=kb_entry.entity_name,
                alternative_names=kb_entry.alternative_names.split('|') if kb_entry.alternative_names else [],
                category=kb_entry.category,
                facts=[]
            )
            entities.append(entity)
        entity.facts.append(Fact(
            book_part_id=kb_entry.book_part_id,
            content=kb_entry.fact,
            sibling_index=kb_entry.sibling_index,
            sibling_total=kb_entry.sibling_total
        ))
    return entities
