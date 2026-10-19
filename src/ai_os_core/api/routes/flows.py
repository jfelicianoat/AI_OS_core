"""Monitor visual: pasos de flujo entre apps, su emisión en vivo y la página /monitor.
Comentarios en español.

Cada petición que recorre el ecosistema lleva un `flow_id`. Las apps informan de sus saltos
(POST /api/v1/flows/hops) y Core añade por su cuenta las decisiones de política y los recibos
que recibe con ese mismo `flow_id`. Sólo metadatos: nunca el texto de la petición.
"""

import asyncio
import json
import logging
import os
import re
from pathlib import Path
from typing import Any, Dict, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel, Field, field_validator

from ai_os_core.api.dependencies import get_flows_repo
from ai_os_core.infrastructure.db.repositories.flows_repo import FlowsRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/flows", tags=["Monitor"])
page_router = APIRouter(tags=["Monitor"])

_MONITOR_DIR = Path(__file__).resolve().parents[2] / "monitor"
_ID = r"^[A-Za-z0-9_.:\-]+$"
_MAX_DETAILS = 4096


class HopRequest(BaseModel):
    flow_id: str = Field(min_length=1, max_length=128, pattern=_ID)
    source_system: str = Field(min_length=1, max_length=64, pattern=_ID)
    target_system: str = Field(min_length=1, max_length=64, pattern=_ID)
    kind: Literal["request", "response", "error"]
    summary: str = Field("", max_length=200)
    details: Dict[str, Any] = {}

    @field_validator("details")
    @classmethod
    def _small(cls, v):
        if len(json.dumps(v)) > _MAX_DETAILS:
            raise ValueError(f"details no puede pasar de {_MAX_DETAILS} bytes: sólo metadatos, nunca el contenido.")
        return v


def reporter(request: Request, fallback: str) -> str:
    """Quién informa: la app del token si lo hay; si no, lo que declare la petición."""
    grant = getattr(request.state, "token_grant", None)
    return (grant.principal if grant and grant.principal else None) or request.headers.get("X-Principal-Id") or fallback


def flow_id_from(data: Dict[str, Any], fallback: str) -> str:
    """El flow_id que trae la app si es válido; si no, uno propio (la operación queda como flujo suelto)."""
    value = data.get("flow_id") if isinstance(data, dict) else None
    return value if isinstance(value, str) and 0 < len(value) <= 128 and re.match(_ID, value) else fallback


def record_safely(repo: FlowsRepository, **step) -> None:
    """El monitor nunca tumba una operación: si anotar el paso falla, se registra y se sigue.

    Un paso igual al último del mismo flujo no se repite: una app que sondea (el runner de
    Agora pregunta por cada tarjeta pendiente en cada vuelta) no inunda el monitor.
    """
    try:
        last = repo.last(step["flow_id"])
        if last and all(last[k] == step.get(k, "") for k in ("kind", "source", "summary")):
            return
        repo.append(**step)
    except Exception:  # noqa: BLE001 — cualquier fallo del registro visual es secundario
        logger.exception("No se pudo anotar el paso de flujo %s", step.get("flow_id"))


@router.post("/hops", status_code=201)
def report_hop(req: HopRequest, repo: FlowsRepository = Depends(get_flows_repo)):
    """Una app informa de que pasa el testigo a otra (o de que lo recibe de vuelta)."""
    last = repo.last(req.flow_id)
    if last and (last["kind"], last["source"], last["target"], last["summary"]) == (
            req.kind, req.source_system, req.target_system, req.summary):
        return last  # una app que sondea un estado terminal no lo duplica
    return repo.append(flow_id=req.flow_id, kind=req.kind, source=req.source_system,
                       target=req.target_system, summary=req.summary, details=req.details)


@router.get("/events")
def list_events(
    after: Optional[int] = Query(None, ge=0),
    limit: int = Query(300, ge=1, le=1000),
    repo: FlowsRepository = Depends(get_flows_repo),
):
    """Sin `after`: los últimos `limit` pasos. Con `after`: los posteriores a ese id."""
    return repo.tail(limit) if after is None else repo.after(after, limit)


@router.get("/apps")
def list_apps(request: Request, repo: FlowsRepository = Depends(get_flows_repo)):
    """Universo de apps para dibujar: registradas (token o políticas) y vistas en flujos.

    Una app vista en un flujo que Core no tiene registrada sale como `known: false`.
    """
    from ai_os_core.app import _load_tokens  # perezoso: app importa este módulo
    registered = {g.principal for g in _load_tokens().values() if g.principal}
    registered |= set(repo.policy_principals())
    seen = set(repo.participants()) - {"core"}
    return [{"app": a, "known": a in registered or a in ("ai_broker", "broker")} for a in sorted(registered | seen)]


@router.get("/stream")
async def stream(request: Request, after: Optional[int] = Query(None, ge=0),
                 repo: FlowsRepository = Depends(get_flows_repo)):
    """Server-Sent Events con cada paso nuevo. Sondea SQLite: vale con varios procesos de Core."""
    last = after if after is not None else await run_in_threadpool(repo.last_id)
    poll = float(os.getenv("AI_OS_MONITOR_POLL_S", "0.5"))
    # Cada conexión dura como mucho esto y la página reconecta en el acto desde el último id.
    # Es corto a propósito: detrás de los middleware HTTP de Core la desconexión del navegador no
    # llega, y sin tope una pestaña cerrada dejaba la conexión viva (y bloqueaba recargar o parar Core).
    max_s = float(os.getenv("AI_OS_MONITOR_MAX_S", "30"))

    async def gen():
        nonlocal last
        idle, alive = 0.0, 0.0
        yield "retry: 2000\n\n"
        while alive < max_s and not await request.is_disconnected():
            rows = await run_in_threadpool(repo.after, last, 200)
            for row in rows:
                last = row["id"]
                yield f"id: {row['id']}\ndata: {json.dumps(row)}\n\n"
            idle = 0.0 if rows else idle + poll
            if idle >= 15:  # latido: los proxies y el navegador no cierran la conexión
                idle = 0.0
                yield ": latido\n\n"
            await asyncio.sleep(poll)
            alive += poll

    return StreamingResponse(gen(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


@router.get("/{flow_id}")
def get_flow(flow_id: str, repo: FlowsRepository = Depends(get_flows_repo)):
    steps = repo.flow(flow_id)
    if not steps:
        raise HTTPException(status_code=404, detail=f"No hay pasos para el flujo '{flow_id}'.")
    return {"flow_id": flow_id, "steps": steps}


@page_router.get("/monitor", include_in_schema=False)
def monitor_page():
    """La página no lleva datos: los pide con el token que el usuario escribe en ella."""
    return FileResponse(_MONITOR_DIR / "index.html", media_type="text/html")


@page_router.get("/monitor/{asset:path}", include_in_schema=False)
def monitor_asset(asset: str):
    path = (_MONITOR_DIR / asset).resolve()
    if not path.is_relative_to(_MONITOR_DIR) or not path.is_file():  # nada fuera de la carpeta del monitor
        raise HTTPException(status_code=404, detail="No existe.")
    return FileResponse(path)
