# api/middleware/auth.py
from __future__ import annotations

from typing import Any, Dict, Set
import httpx
from cachetools import TTLCache
from fastapi import Depends, HTTPException, Request, status
from jose import jwt
from jose.exceptions import ExpiredSignatureError, JWTError
from config.keycloak_settings import SETTINGS

# Cache JWKS 5 minutes
_jwks_cache: TTLCache[str, dict] = TTLCache(maxsize=2, ttl=300)

async def _get_jwks() -> dict:
    if "jwks" in _jwks_cache:
        return _jwks_cache["jwks"]
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get(SETTINGS.jwks_url)
        r.raise_for_status()
        jwks = r.json()
        _jwks_cache["jwks"] = jwks
        return jwks

def _extract_bearer(request: Request) -> str:
    auth = request.headers.get("Authorization") or request.headers.get("authorization")
    if not auth or not auth.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing bearer token")
    return auth.split(" ", 1)[1].strip()

async def verify_token(request: Request) -> Dict[str, Any]:
    # ⚠️ Laisser passer le pré-vol CORS
    if request.method == "OPTIONS":
        return {"skip": True}

    token = _extract_bearer(request)
    jwks = await _get_jwks()

    header = jwt.get_unverified_header(token)
    kid = header.get("kid")
    key = None
    for k in jwks.get("keys", []):
        if k.get("kid") == kid:
            key = k
            break

    try:
        payload = jwt.decode(
            token,
            key,  # JWK dict accepté par python-jose
            algorithms=["RS256", "RS384", "RS512", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512"],
            issuer=SETTINGS.issuer,
            audience=list(SETTINGS.accepted_audiences) if SETTINGS.accepted_audiences else None,
            options={"verify_aud": bool(SETTINGS.accepted_audiences)},
            leeway=SETTINGS.leeway,
        )
    except ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"Invalid token: {e}")

    return payload

def _roles_from_payload(payload: Dict[str, Any]) -> Set[str]:
    roles = set(payload.get("realm_access", {}).get("roles", []) or [])
    resource_access = payload.get("resource_access") or {}
    for _, data in resource_access.items():
        roles.update(data.get("roles", []) or [])
    return roles

def require_roles(*required: str):
    required_set = set(required)
    async def _dep(request: Request, payload: Dict[str, Any] = Depends(verify_token)):
        # OPTIONS déjà autorisé
        if request.method == "OPTIONS":
            return payload
        roles = _roles_from_payload(payload)
        missing = required_set - roles
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing roles: {', '.join(sorted(missing))}"
            )
        return payload
    return _dep
