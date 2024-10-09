
from backend.database import SessionLocal
from backend.models.kb_entries import KnowledgeBaseEntry
from backend.tasks.knowledge_base_building import build_knowledge_base, format_knowledge_base_entities, get_knowledge_base_entries, group_knowledge_base_entries


if __name__ == '__main__':
    # build_knowledge_base(book_id="63892733-821f-42f9-a15f-c629025b6770")
    db = SessionLocal()
    try:
        book_id = "2ec96cae-17b5-4961-a7f9-1b35c2c24d28"
        kb_entries = db.query(KnowledgeBaseEntry).filter(KnowledgeBaseEntry.book_id == book_id).order_by(KnowledgeBaseEntry.created_at).all()
        merged_kb = group_knowledge_base_entries(kb_entries)
        kb_str = format_knowledge_base_entities(merged_kb, max_entries_per_name=5)

        print(kb_str)
    finally:
        db.close()
