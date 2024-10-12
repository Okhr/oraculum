
from backend.database import SessionLocal
from backend.models.kb_entries import KnowledgeBaseEntry
from backend.tasks.knowledge_base_building import build_knowledge_base, format_knowledge_base_entities, get_knowledge_base_entries, group_knowledge_base_entries


if __name__ == '__main__':
    build_knowledge_base(book_id="2806be0c-0ffc-4228-9c4c-38836ee3133e")
