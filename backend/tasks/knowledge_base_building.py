import json
import os
import re
import time
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langfuse import Langfuse
from langfuse.decorators import langfuse_context, observe
from langfuse.openai import OpenAI
from tqdm import tqdm

from backend.database import SessionLocal
from backend.models.summaries import Summary
from backend.models.users import User
from backend.models.books import Book
from backend.models.book_parts import BookPart
from backend.models.kb_entries import KnowledgeBaseEntry

load_dotenv(override=True)
client = OpenAI()
languse = Langfuse()

with open(f'core/prompts/fr.json', 'r') as f:
    data = json.load(f)
    entity_summarization_with_kb_prompt = data['entity_summarization_with_kb_prompt']


@observe()
def build_knowledge_base(book_id: str):
    print(f'[Starting knowledge building task] book_id : {book_id}')

    db = SessionLocal()

    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        user = db.query(User).filter(User.id == book.user_id).first()

        langfuse_context.update_current_trace(
            metadata={"book_id": book_id, "book_title": book.title, "user_id": user.id, "user_name": user.name},
            tags=["knowledge_building"],
            user_id=user.name,
        )

        book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()
        sorted_book_parts = sort_book_parts(book_parts)

        for book_part in sorted_book_parts:
            if book_part.is_story_part and not book_part.is_entity_extracted:

                extract_entities_from_sub_parts(book_part)
                summarize_sub_parts(book_part)
                # OTHER EXTRACTIONS

                book_part.is_entity_extracted = True
                db.commit()
            else:
                print(f"Skipping book part : {book_part.label}")
    finally:
        db.close()


def extract_entities_from_sub_parts(book_part: BookPart):
    print(f"[Knowledge building task] Extracting entities for book part : {book_part.label}")

    db = SessionLocal()

    # split content into sub parts
    content = re.sub(r'\n{4,}', '\n\n\n', book_part.content)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.environ.get("CHUNK_SIZE")),
        chunk_overlap=int(os.environ.get("CHUNK_OVERLAP")),
        length_function=len,
        separators=["\n\n\n", "\n\n", "\n", ".", ",", " ", ""],
        keep_separator=True,
    )

    sub_parts = text_splitter.split_text(content)

    for i, sub_part in enumerate(sub_parts):
        filtered_kb = get_knowledge_base_entries(book_part.book_id, sub_part)
        merged_kb = merge_knowledge_base_entries(filtered_kb, max_entries_per_name=5)
        kb_str = format_knowledge_base_entities(merged_kb)        

        prompt = languse.get_prompt("sub_part_entity_extraction", label="latest")
        computed_prompt = prompt.compile(knowledge_base=kb_str, text_part=sub_part)

        MOCK = False

        if MOCK:
            # Mock response for testing purposes
            time.sleep(0.2)  # Simulate a delay
            json_output = [
                {
                    "entity": "Entity 1",
                    "alternative_names": ["Alt Name 1", "Alt Name 2"],
                    "referenced_entity": "Referenced Entity 1",
                    "category": "Category 1",
                    "summary": "Summary of Entity 1"
                },
                {
                    "entity": "Entity 2",
                    "alternative_names": ["Alt Name 3", "Alt Name 4"],
                    "referenced_entity": "Referenced Entity 2",
                    "category": "Category 2",
                    "summary": "Summary of Entity 2"

                }
            ]
        else:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": computed_prompt}
                ],
                response_format={"type": "json_object"}
            )
            json_output = json.loads(completion.choices[0].message.content)

        for entry in json_output['entities']:
            new_entry = KnowledgeBaseEntry(
                book_id=book_part.book_id,
                book_part_id=book_part.id,
                entity_name=entry['entity_name'],
                alternative_names='|'.join(entry['alternative_names']) if entry.get('alternative_names', []) else None,
                referenced_entity_name=entry.get('referenced_entity') if (entry.get('referenced_entity') and entry['referenced_entity'] != "") else None,
                category=entry['category'],
                fact=entry['summary'],
                sibling_index=i,
                sibling_total=len(sub_parts)
            )
            db.add(new_entry)
            db.commit()


def summarize_sub_parts(book_part: BookPart):
    print(f"[Knowledge building task] Summarizing sub parts for book part : {book_part.label}")

    db = SessionLocal()

    # split content into sub parts
    content = re.sub(r'\n{4,}', '\n\n\n', book_part.content)
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=int(os.environ.get("CHUNK_SIZE")),
        chunk_overlap=int(os.environ.get("CHUNK_OVERLAP")),
        length_function=len,
        separators=["\n\n\n", "\n\n", "\n", ".", ",", " ", ""],
        keep_separator=True,
    )

    sub_parts = text_splitter.split_text(content)

    for i, sub_part in enumerate(sub_parts):
        prompt = languse.get_prompt("sub_part_summarization", label="latest")
        computed_prompt = prompt.compile(text_part=sub_part)

        MOCK = False

        if MOCK:
            # Mock response for testing purposes
            time.sleep(0.2)  # Simulate a delay
            summary = "This is a mock summary for the sub part."
        else:
            completion = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "user", "content": computed_prompt}
                ]
            )
            summary = completion.choices[0].message.content.strip()

        new_summary = Summary(
            book_id=book_part.book_id,
            book_part_id=book_part.id,
            content=summary,
            sibling_index=i,
            sibling_total=len(sub_parts)
        )
        db.add(new_summary)
        db.commit()


def sort_book_parts(book_parts: list[BookPart]):
    sorted_book_parts = []
    root_book_parts = [book_part for book_part in book_parts if book_part.parent_id is None and book_part.is_story_part]
    root_book_parts = sorted(root_book_parts, key=lambda x: x.sibling_index)

    for root_book_part in root_book_parts:
        sorted_book_parts.append(root_book_part)
        sorted_book_parts.extend(sort_book_parts_recursive(root_book_part, book_parts))
    return sorted_book_parts


def sort_book_parts_recursive(book_part: BookPart, book_parts: list[BookPart]):
    child_book_parts = [child for child in book_parts if child.parent_id == book_part.id and child.is_story_part]
    child_book_parts = sorted(child_book_parts, key=lambda x: x.sibling_index)
    sorted_book_parts = []

    for child_book_part in child_book_parts:
        sorted_book_parts.append(child_book_part)

        sorted_book_parts.extend(sort_book_parts_recursive(child_book_part, book_parts))
    return sorted_book_parts


def get_knowledge_base_entries(book_id: str, content: str):
    db = SessionLocal()
    try:
        filtered_kb_entries = []
        kb_entries = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.book_id == book_id).all()
        for kb_entry in kb_entries:
            if (kb_entry.entity_name.strip().lower() in content.lower()
                or (kb_entry.referenced_entity_name and kb_entry.referenced_entity_name.strip().lower() in content.lower())
                    or (kb_entry.alternative_names and any(name.strip().lower() in content.lower() for name in kb_entry.alternative_names.split("|")))):
                filtered_kb_entries.append(kb_entry)
        return filtered_kb_entries
    finally:
        db.close()


def merge_knowledge_base_entries(kb_entries: list[KnowledgeBaseEntry], max_entries_per_name: int = 3):
    merged_kb_entries = {}

    for kb_entry in kb_entries:
        entity_name = kb_entry.entity_name.strip()

        if entity_name in merged_kb_entries:
            merged_kb_entries[entity_name].append(kb_entry)
            if len(merged_kb_entries[entity_name]) > max_entries_per_name:
                merged_kb_entries[entity_name] = merged_kb_entries[entity_name][-max_entries_per_name:]
        else:
            merged_kb_entries[entity_name] = [kb_entry]

    return merged_kb_entries


def format_knowledge_base_entities(merged_kb_entries: dict[str, list[KnowledgeBaseEntry]]) -> str:
    entries_dict = {}
    for k, v in merged_kb_entries.items():
        entries = []
        for entry in v:
            # get the associated book_part label
            db = SessionLocal()
            try:
                book_part_label = db.query(BookPart).filter(BookPart.id == entry.book_part_id).first().label.strip()
            finally:
                db.close()
            
            entries.append({
            "alternative_names": entry.alternative_names.split("|") if entry.alternative_names else [],
            "category": entry.category,
            "fact": entry.fact,
            "chapter_name": book_part_label,
            "chapter_sub_part": f"{entry.sibling_index+1}/{entry.sibling_total}"
        })
        entries_dict[k] = entries

    return json.dumps(entries_dict, indent=4)
