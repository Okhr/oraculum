import ebooklib
import re
from task_queue.main import h
from backend.database import SessionLocal
from backend.models.users import User
from backend.models.books import Book
from backend.models.book_parts import BookPart
from core.parsing import extract_structured_toc

EXCLUDE_LABELS = [r'^couverture$', r'^titre$', r'^avant-propos', r'^préface', r'^postface', r'^biographie$', r'^bibliographie$', r'^du même auteur$', r'^mentions légales$',
                  r'^remerciements$', r'^copyright$', r'^droit d(’|\')auteur$', r'^dans la même collection$', r'^table des matières$', r'^note de l(’|\')auteure*$', r'^quatrième de couverture$']


@h.task()
def extract_text_parts_task(book: ebooklib.epub.EpubBook, book_id: str):
    content = extract_structured_toc(book)
    db = SessionLocal()

    try:
        def iterate_text_parts(node, sibling_index, parent_id=None):
            # Check the part label to infer if it's part of the story
            is_story_part = not any(re.match(pattern, node['label'], re.IGNORECASE) for pattern in EXCLUDE_LABELS)

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
