import ebooklib
from backend.database import SessionLocal
from backend.models.users import User
from backend.models.books import Book
from backend.models.text_parts import TextPart
from core.parsing import extract_structured_toc


def extract_text_parts_task(book: ebooklib.epub.EpubBook, user_id: str, book_id: str):
    content = extract_structured_toc(book)
    db = SessionLocal()

    try:
        def iterate_text_parts(node, parent_id=None):
            book_part = TextPart(
                user_id=user_id,
                book_id=book_id,
                parent_id=parent_id,
                toc_id=node['id'],
                label=node['label'],
                content=node['content']
            )

            db.add(book_part)
            db.commit()

            for child in node['children']:
                iterate_text_parts(child, parent_id=book_part.id)

        for part in content:
            iterate_text_parts(part)

        # Update the is_parsed property
        book_to_update = db.query(Book).filter(Book.id == book_id).first()
        if book_to_update:
            book_to_update.is_parsed = True
            db.commit()
        else:
            raise ValueError("Book with the provided ID was not found in the database.")

    finally:
        db.close()
