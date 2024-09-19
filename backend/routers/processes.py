from fastapi import APIRouter


router = APIRouter()

@router.get("/entity_extractions/")
async def get_entity_extractions():
    pass
