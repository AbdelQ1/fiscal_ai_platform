# api/routes/espocrm.py
from __future__ import annotations

from fastapi import APIRouter, Depends
from api.middleware.auth import require_roles

router = APIRouter(prefix="/espocrm", tags=["espocrm"])

@router.get("/dossiers", dependencies=[Depends(require_roles("espocrm.read"))])
async def get_dossiers() -> dict:
    # TODO: branchement EspoCRM réel ici
    dossiers = [
        {"id": "DUB-2024", "titre": "Dossier Dubois - 2024"},
        {"id": "MAR-SCI", "titre": "Dossier Martin - SCI Valoris"},
        {"id": "BEN-TVA", "titre": "Dossier Benali - TVA"},
    ]
    return {"ok": True, "dossiers": dossiers}
