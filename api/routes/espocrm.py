# api/routes/espocrm.py
from __future__ import annotations
from fastapi import APIRouter, Depends
from typing import Any, Dict, List

# Dépendance d'auth optionnelle : on la prend si elle existe, sinon on no-op
try:
    from api.middleware.auth import require_roles  # type: ignore
except Exception:
    def require_roles(*_roles: str):
        async def _noop() -> Dict[str, Any]:
            return {}
        return _noop

router = APIRouter(prefix="/espocrm", tags=["espocrm"])

@router.get("/dossiers")
async def list_dossiers(_: Dict[str, Any] = Depends(require_roles("espocrm.read"))):
    """
    Mock de validation du pipeline côté front.
    Remplace temporairement l'appel réel à EspoCRM.
    """
    return {
        "dossiers": [
            {"id": "d1", "titre": "Dossier Dubois - 2024"},
            {"id": "d2", "titre": "Dossier Martin - SCI Valoris"},
            {"id": "d3", "titre": "Dossier Benali - TVA"},
        ]
    }
