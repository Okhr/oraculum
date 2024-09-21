import io
from ebooklib import epub
import re
import dramatiq
from backend.database import SessionLocal
from backend.models.users import User
from backend.models.books import Book
from backend.models.book_parts import BookPart
from core.parsing import extract_structured_toc

EXCLUDE_LABELS = [r'^couverture$', r'^titre$', r'^avant-propos', r'^préface', r'^postface', r'^biographie$', r'^bibliographie$', r'^du même auteur$', r'^mentions légales$',
                  r'^remerciements$', r'^copyright$', r'^droit d(’|\')auteur$', r'^dans la même collection$', r'^table des matières$', r'^note de l(’|\')auteure*$', r'^quatrième de couverture$']


@dramatiq.actor(max_retries=0, time_limit=60*60*1000)
def extract_book_parts_task(book_id: str):
    db = SessionLocal()

    book_file = db.query(Book).filter(Book.id == book_id).first()

    if book_file:
        book = epub.read_epub(io.BytesIO(book_file.file_data))
    else:
        raise ValueError("Book with the provided ID was not found in the database.")

    content = extract_structured_toc(book)

    try:
        def iterate_text_parts(node, sibling_index, parent_id=None):
            # Check the part label to infer if it's part of the story
            is_story_part = not any(re.match(pattern, node['label'], re.IGNORECASE) for pattern in EXCLUDE_LABELS)

            # Check if the text_part is already present in the database
            existing_book_part = db.query(BookPart).filter(
                BookPart.book_id == book_id,
                BookPart.parent_id == parent_id,
                BookPart.toc_id == node['id'],
                BookPart.label == node['label'],
                BookPart.content == node['content'],
                BookPart.sibling_index == sibling_index,
            ).first()

            if not existing_book_part:
                book_part = BookPart(
                    book_id=book_id,
                    parent_id=parent_id,
                    toc_id=node['id'],
                    label=node['label'],
                    content=node['content'],
                    sibling_index=sibling_index,
                    is_story_part=is_story_part,
                )

                db.add(book_part)
                db.commit()
            else:
                book_part = existing_book_part
                print(f"BookPart with toc_id : {node['id']}, label : {node['label']} already exists in the database.")

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
