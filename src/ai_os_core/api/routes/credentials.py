"""Credencial del AI Broker repartida por Core: ninguna app guarda ni pide a mano su token.

El Broker rota su token de administración en cada arranque y lo publica en el llavero del
PC IA. El runner de Agora vive allí: lo lee y lo publica aquí (PUT) en cuanto cambia, y
cada minuto por si Core se ha reiniciado. Las apps lo piden (GET) con su token de Core y,
si el Broker les responde 401/403, lo vuelven a pedir.

Se guarda sólo en memoria, nunca en la base: si Core se reinicia, el runner lo repone en
su siguiente vuelta.
"""

import threading
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api/v1/credentials", tags=["Credentials"])

# Sólo quien vive junto al Broker puede publicar su token (o el director, para pruebas)
PUBLISHERS = {"agora"}

_lock = threading.Lock()
_broker: dict = {}


class BrokerCredential(BaseModel):
    token: str = Field(min_length=8, max_length=512)


def _principal(request: Request):
    grant = getattr(request.state, "token_grant", None)
    return grant.principal if grant is not None else None


@router.put("/broker")
def publish_broker_token(body: BrokerCredential, request: Request):
    principal = _principal(request)
    if principal is not None and principal not in PUBLISHERS:
        raise HTTPException(status_code=403, detail=f"'{principal}' no puede publicar el token del AI Broker.")
    with _lock:
        changed = _broker.get("token") != body.token
        if changed:
            _broker.update(
                token=body.token,
                updated_at=datetime.now(timezone.utc).isoformat(),
                published_by=principal or "director",
            )
        return {"changed": changed, "updated_at": _broker["updated_at"]}


@router.get("/broker")
def read_broker_token():
    with _lock:
        if not _broker:
            raise HTTPException(
                status_code=503,
                detail="Core aún no tiene el token del AI Broker: lo publica el runner de Agora del PC IA al arrancar.",
            )
        return dict(_broker)


def reset_for_tests() -> None:
    with _lock:
        _broker.clear()
