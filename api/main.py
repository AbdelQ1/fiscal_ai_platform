from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
import logging

app = FastAPI(title="Fiscal Local API")
logger = logging.getLogger("uvicorn")
logging.basicConfig(level=logging.INFO)

# CORS: autoriser l’UI Vite (5173)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

@app.get("/")
def root():
    return {"name": "Fiscal Local API", "version": "0.2.0"}

@app.get("/ui/ping")
def ui_ping():
    return "ok"

# --- Endpoints de démo protégé/optionnels -----------------
@app.get("/espocrm/dossiers")
def get_dossiers(authorization: Optional[str] = Header(None)):
    # Si tu veux exiger un vrai token, décommente la ligne suivante :
    # if not authorization: raise HTTPException(status_code=401, detail="Missing bearer token")
    return {
        "dossiers": [
            {"id": "DUBOIS-2024", "title": "Dossier Dubois - 2024"},
            {"id": "MARTIN-SCI", "title": "Dossier Martin - SCI Valoris"},
            {"id": "BENALI-TVA", "title": "Dossier Benali - TVA"},
        ]
    }

@app.get("/files/list")
def files_list(authorization: Optional[str] = Header(None)):
    return {
        "files": [
            {"name": "Facture-ACME-2024.pdf", "size": 128934, "uploaded_at": "2025-08-01T10:40:00Z"},
            {"name": "Releve-Banque-Juin.csv", "size": 40960, "uploaded_at": "2025-08-07T09:12:00Z"},
        ]
    }
