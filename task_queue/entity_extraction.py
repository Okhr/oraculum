import json
import os
from pprint import pp
import re
from dotenv import load_dotenv
import dramatiq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from openai import OpenAI
from tqdm import tqdm

from backend.database import SessionLocal
from backend.models.users import User
from backend.models.books import Book
from backend.models.book_parts import BookPart
from backend.models.kb_entries import KnowledgeBaseEntry


@dramatiq.actor(max_retries=0)
def extract_entities_task(book_id: str):
    load_dotenv()

    client = OpenAI(
        api_key=os.environ.get("OPENAI_API_KEY")
    )

    with open(f'core/prompts/fr.json', 'r') as f:
        data = json.load(f)
        entity_summarization_with_kb_prompt = data['entity_summarization_with_kb_prompt']
    db = SessionLocal()

    try:
        book_parts = db.query(BookPart).filter(BookPart.book_id == book_id).all()
        sorted_book_parts = sort_book_parts(book_parts)

        for book_part in sorted_book_parts:
            if book_part.is_story_part and not book_part.is_entity_extracted:
                print(f"Extracting entities for book part : {book_part.label}")
                content = re.sub(r'\n{4,}', '\n\n\n', book_part.content)

                # split content into sub parts
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=10000,
                    chunk_overlap=0,
                    length_function=len,
                    separators=["\n\n\n", "\n\n", "\n", ".", ",", " ", ""],
                    keep_separator=True,
                )

                sub_parts = text_splitter.split_text(content)

                for i, sub_part in enumerate(tqdm(sub_parts)):
                    filtered_kb = get_knowledge_base_entries(book_id, sub_part)
                    merged_kb = merge_knowledge_base_entries(filtered_kb, max_entries_per_name=5)
                    kb_str = format_knowledge_base_entities(merged_kb)
                    computed_prompt = entity_summarization_with_kb_prompt["prompt"].format(knowledge_base=kb_str, text_part=sub_part)

                    max_retries = 3
                    for attempt in range(max_retries):
                        try:
                            completion = client.chat.completions.create(
                                model="gpt-4o-mini",
                                messages=[
                                    {"role": "user", "content": computed_prompt}
                                ]
                            )
                            break
                        except Exception as e:
                            print(f"Attempt {attempt + 1} failed. Retrying...")
                            if attempt == max_retries - 1:
                                print(f"Max retries exceeded. Failed to get a response. Error: {e}")
                                raise

                    json_output = parse_json_output(completion.choices[0].message.content)

                    for entry in json_output:
                        new_entry = KnowledgeBaseEntry(
                            book_id=book_id,
                            book_part_id=book_part.id,
                            entity_name=entry['entity'],
                            alternative_names=','.join(entry.get('alternative_names', [])),
                            referenced_entity_name=entry.get('referenced_entity', ''),
                            category=entry['category'],
                            fact=entry['summary'],
                            sibling_index=i,
                            sibling_total=len(sub_parts)
                        )
                        db.add(new_entry)

                # set the book part as entity extracted
                book_part.is_entity_extracted = True
                db.commit()

            else:
                print(f"Skipping book part : {book_part.label}")
        return book_id

    finally:
        db.close()


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
                or (kb_entry.referenced_entity_name != "" and kb_entry.referenced_entity_name.strip().lower() in content.lower())
                    or (kb_entry.alternative_names != "" and any(name.strip().lower() in content.lower() for name in kb_entry.alternative_names.split(",")))):
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
    with open(f'core/prompts/fr.json', 'r') as f:
        data = json.load(f)
        kb_entity_template = data['kb_entity_template']
        kb_entry_template = data['kb_entry_template']

    formatted_entities = []
    for entity_name, entries in merged_kb_entries.items():

        entry_strings = []
        for entry in entries:
            # get the associated book_part label
            db = SessionLocal()
            try:
                book_part_label = db.query(BookPart).filter(BookPart.id == entry.book_part_id).first().label.strip()
            finally:
                db.close()
            entry_strings.append(kb_entry_template["template"].format(category=entry.category, label=book_part_label, sibling_index=entry.sibling_index,
                                 sibling_total=entry.sibling_total, alternative_names=entry.alternative_names, fact=entry.fact))
        formatted_entities.append(kb_entity_template["template"].format(entity_name=entity_name, entries="\n\n".join(entry_strings)))

    return "\n\n".join(formatted_entities)


def parse_json_output(llm_response: str) -> dict:
    json_str = re.search(r'\[.*\]', llm_response, re.DOTALL)
    if json_str:
        json_str = json_str.group(0)
        return json.loads(json_str)
    else:
        raise ValueError("No JSON list object found in the LLM response")
