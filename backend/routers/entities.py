from backend.models.book_parts import BookPart
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
from backend.tasks.knowledge_base_building import group_knowledge_base_entries

router = APIRouter()


@router.get("/book_id/{book_id}")
async def get_book_entities(book_id: str, current_user: Annotated[UserResponseSchema, Depends(auth.get_current_user)], db: Session = Depends(get_db)) -> List[EntityResponseSchema]:
    kb_entries = db.query(KnowledgeBaseEntry).filter(
        KnowledgeBaseEntry.book_id == book_id,
        KnowledgeBaseEntry.sibling_index.is_(None),
        KnowledgeBaseEntry.sibling_total.is_(None)
    ).order_by(KnowledgeBaseEntry.created_at).all()
    book = db.query(Book).filter(Book.id == book_id).first()

    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    if not kb_entries:
        raise HTTPException(status_code=404, detail="Knowledge base entries not found")

    if book.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="The book does not belong to the current user")

    book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()

    if not book_parts:
        raise HTTPException(status_code=404, detail="Book parts not found")

    book_parts_content = {bp.id: bp.content for bp in book_parts}

    # Group the entries
    grouped_kb_entries = group_knowledge_base_entries(kb_entries)

    entities = []
    for entity_name, v in grouped_kb_entries.items():
        entity = EntityResponseSchema(
            name=entity_name,
            alternative_names=v["alternative_names"],
            category=v["category"],
            facts=[Fact(
                book_part_id=entry.book_part_id,
                content=entry.fact,
                # TODO : avoid overlaps in the occurrences
                occurrences=sum([book_parts_content[entry.book_part_id].lower().count(name.lower()) for name in [entity_name] + v["alternative_names"]]),
                sibling_index=None,
                sibling_total=None
            ) for entry in v["entries"]]
        )
        entities.append(entity)
    return entities
