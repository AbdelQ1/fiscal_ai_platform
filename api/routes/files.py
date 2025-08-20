# api/routes/files.py
from __future__ import annotations
from fastapi import APIRouter, Depends
from typing import Any, Dict, List

try:
    from api.middleware.auth import require_roles  # type: ignore
except Exception:
    def require_roles(*_roles: str):
        async def _noop() -> Dict[str, Any]:
            return {}
        return _noop

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/list")
async def list_files(_: Dict[str, Any] = Depends(require_roles("files.read"))):
    """
    Mock de validation. Remplace ton implémentation qui lisait le disque / DB.
    """
    return {
        "files": [
            {"name": "Facture Batterie Bosch.pdf", "size": 123456},
            {"name": "Facture MCA Syno RAM 8G 2024.pdf", "size": 234567},
        ]
    }
