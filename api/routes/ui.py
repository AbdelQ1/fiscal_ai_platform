# api/routes/ui.py
from fastapi import APIRouter

router = APIRouter(prefix="/ui", tags=["ui"])

@router.get("/ping")
async def ping():
    return {"status": "ok"}
