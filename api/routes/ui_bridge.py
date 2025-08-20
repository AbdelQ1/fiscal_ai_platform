from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/ui/ping")
def ping_ui():
    return JSONResponse({"status": "ok"})
