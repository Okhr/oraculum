import ebooklib
from backend.database import SessionLocal
from backend.models.users import User
from backend.models.books import Book
from backend.models.text_parts import TextPart
from core.parsing import extract_structured_toc


def extract_text_parts_task(book: ebooklib.epub.EpubBook, book_id: str):
    content = extract_structured_toc(book)
    db = SessionLocal()

    try:
        def iterate_text_parts(node, sibling_index, parent_id=None):
            book_part = TextPart(
                book_id=book_id,
                parent_id=parent_id,
                toc_id=node['id'],
                label=node['label'],
                content=node['content'],
                sibling_index=sibling_index,
            )

            db.add(book_part)
            db.commit()

            for i, child in enumerate(node['children']):
                iterate_text_parts(child, i, parent_id=book_part.id)

        for i, part in enumerate(content):
            iterate_text_parts(part, i)

        # Update the is_parsed property
        book_to_update = db.query(Book).filter(Book.id == book_id).first()
        if book_to_update:
            book_to_update.is_parsed = True
            db.commit()
        else:
            raise ValueError("Book with the provided ID was not found in the database.")

    finally:
        db.close()
