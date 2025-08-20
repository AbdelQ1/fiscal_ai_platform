from fastapi import APIRouter
from pydantic import BaseModel
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/ai", tags=["ai"])

class QueryIn(BaseModel):
    prompt: str

@router.post("/query")
async def ai_query(body: QueryIn):
    # TODO: brancher ton LLM local (Ollama/Mistral) ici
    mock = f"Résumé: (mock) — J'ai bien reçu: «{body.prompt[:120]}»"
    return JSONResponse({"ok": True, "answer": mock})
