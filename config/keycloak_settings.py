# config/keycloak_settings.py
from pydantic import BaseModel
import os

class KeycloakSettings(BaseModel):
    # Issuer du realm
    issuer: str = os.getenv("KEYCLOAK_ISSUER", "http://localhost:8081/realms/fiscal-local")
    # URL JWKS (clé publique). Si None, dérivée depuis issuer
    jwks_url: str | None = os.getenv("KEYCLOAK_JWKS_URL", None)
    # Audiences acceptées (SPA: fiscal-ui; sinon mets fiscal-api si tu crées un client backend)
    accepted_audiences: set[str] = set(os.getenv("KEYCLOAK_AUDIENCES", "fiscal-ui").split(","))
    # Tolérance d’horloge (sec)
    leeway: int = int(os.getenv("KEYCLOAK_LEEWAY", "30"))

SETTINGS = KeycloakSettings()
if SETTINGS.jwks_url is None:
    SETTINGS.jwks_url = f"{SETTINGS.issuer}/protocol/openid-connect/certs"
