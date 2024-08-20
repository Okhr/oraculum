import rq
import ebooklib
from sqlalchemy.orm import Session
from backend.models.text_parts import BookPart
from core.parsing import extract_structured_toc

def extract_text_parts_task(book: ebooklib.epub.EpubBook, user_id: str, book_id: str, session: Session):
    content = extract_structured_toc(book)

    def iterate_text_parts(node, parent_id=None):
        book_part = BookPart(
            user_id=user_id,
            book_id=book_id,
            parent_id=parent_id,
            toc_id=node['id'],
            label=node['label'],
            content=node['content']
        )
        session.add(book_part)
        session.commit()

        for child in node['children']:
            iterate_text_parts(child, parent_id=book_part.id)

    for part in content:
        iterate_text_parts(part)
