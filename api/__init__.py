from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import ui_bridge, files, ai, espocrm_bridge

app = FastAPI(title="Fiscal AI Platform")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ui_bridge.router)
app.include_router(files.router)
app.include_router(ai.router)
app.include_router(espocrm_bridge.router)
