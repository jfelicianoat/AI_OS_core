"""Lanzador del ecosistema: qué apps están vivas y arrancarlas desde el monitor.
Comentarios en español.

El catálogo es un fichero JSON (`AI_OS_APPS_FILE`, por defecto `config/apps.json` junto al
repo) que dice, por app, cómo se arranca, cómo se sabe si está viva y de qué depende:
- `requires`: sin ellas vivas la app no se puede arrancar (p. ej. Gestión Tareas IA y Agora);
- `uses`: las usa, pero puede arrancar sin ellas (se avisa).
Core sólo ejecuta lo que dice el catálogo en disco, nunca un comando que llegue en la petición,
y sólo el token común (director) puede arrancar: el token de una app no arranca a las demás.
"""

import json
import logging
import os
import ssl
import subprocess
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai_os_core.api.dependencies import get_flows_repo
from ai_os_core.api.routes.flows import record_safely
from ai_os_core.infrastructure.db.repositories.flows_repo import FlowsRepository

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/apps", tags=["Lanzador"])

_DEFAULT_CATALOG = Path(__file__).resolve().parents[4] / "config" / "apps.json"
_HEALTH_TIMEOUT_S = 1.5
_PROCESS_CACHE_S = 3.0
_process_cache: Dict[str, Any] = {"at": 0.0, "procs": []}


def load_catalog() -> List[Dict[str, Any]]:
    """Las apps del catálogo; sin fichero, ninguna (el monitor lo dice y sigue funcionando)."""
    path = Path(os.getenv("AI_OS_APPS_FILE") or _DEFAULT_CATALOG)
    if not path.is_file():
        return []
    apps = json.loads(path.read_text(encoding="utf-8")).get("apps", [])
    return [a for a in apps if isinstance(a, dict) and a.get("id")]


def _processes() -> List[Tuple[int, str]]:
    """(PID, línea de comando en minúsculas) de los procesos vivos (Windows), en caché unos segundos."""
    now = time.monotonic()
    if now - _process_cache["at"] < _PROCESS_CACHE_S:
        return _process_cache["procs"]
    procs: List[Tuple[int, str]] = []
    if sys.platform == "win32":
        # shortcut: sólo Windows (el TFM vive ahí); en otro sistema sólo cuenta la URL de salud
        try:
            out = subprocess.run(
                ["powershell.exe", "-NoProfile", "-Command",
                 "Get-CimInstance Win32_Process | Where-Object CommandLine | "
                 "Select-Object ProcessId,CommandLine | ConvertTo-Json -Compress"],
                capture_output=True, text=True, timeout=10, creationflags=subprocess.CREATE_NO_WINDOW,
            ).stdout
            data = json.loads(out or "[]")
            data = data if isinstance(data, list) else [data]
            procs = [(int(p["ProcessId"]), str(p["CommandLine"]).lower()) for p in data]
        except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
            logger.exception("No se pudo listar los procesos")
    _process_cache.update(at=now, procs=procs)
    return procs


def _command_lines() -> List[str]:
    return [line for _, line in _processes()]


def _marks(app: Dict[str, Any]) -> List[str]:
    marks = app.get("match") or []
    return [m.lower() for m in ([marks] if isinstance(marks, str) else marks)]


def _health_answers(url: str) -> bool:
    """Viva si contesta algo por HTTP (un 401 del tablero de Agora también es que está ahí)."""
    ctx = ssl.create_default_context()
    ctx.check_hostname, ctx.verify_mode = False, ssl.CERT_NONE  # sólo se mira si contesta: certificados propios
    try:
        with urllib.request.urlopen(url, timeout=_HEALTH_TIMEOUT_S, context=ctx):
            return True
    except urllib.error.HTTPError as exc:
        return exc.code < 500
    except (OSError, ValueError):
        return False


def _alive(app: Dict[str, Any], lines: List[str]) -> bool:
    if app.get("health"):
        return _health_answers(app["health"])
    return any(m in line for m in _marks(app) for line in lines)


def statuses() -> Dict[str, Any]:
    """Estado de todo el catálogo: viva o no, y qué le falta para poder arrancar."""
    catalog = load_catalog()
    lines = _command_lines() if any(not a.get("health") for a in catalog) else []
    with ThreadPoolExecutor(max_workers=8) as pool:
        alive = dict(zip([a["id"] for a in catalog], pool.map(lambda a: _alive(a, lines), catalog)))
    names = {a["id"]: a.get("name", a["id"]) for a in catalog}
    result = []
    for app in catalog:
        missing = [d for d in app.get("requires", []) if not alive.get(d)]
        needed_by = [names[o["id"]] for o in catalog if app["id"] in o.get("requires", []) and alive.get(o["id"])]
        result.append({
            "id": app["id"], "name": app.get("name", app["id"]), "kind": app.get("kind", "local"),
            "running": alive[app["id"]], "requires": app.get("requires", []), "uses": app.get("uses", []),
            "can_start": (app.get("kind", "local") != "remote" and bool(app.get("start"))
                          and not missing and not alive[app["id"]]),
            "blocked_by": [names.get(d, d) for d in missing],
            # Se para buscando su proceso: sin `match` (o remota) Core no sabe cuál es
            "can_stop": app.get("kind", "local") != "remote" and bool(_marks(app)) and alive[app["id"]],
            "needed_by": needed_by,
            "warnings": [names.get(d, d) for d in app.get("uses", []) if not alive.get(d)],
            "note": app.get("note", ""),
        })
    return {"apps": result, "checked_at": datetime.now(timezone.utc).isoformat()}


def _token_for(principal: Optional[str]) -> str:
    from ai_os_core.app import _load_tokens  # perezoso: app importa este módulo
    tokens = _load_tokens()
    for token, grant in tokens.items():
        if principal and grant.principal == principal:
            return token
    return os.getenv("AI_OS_API_TOKEN", "")


def _spawn(command: List[str], cwd: Optional[str], env: Dict[str, str]) -> None:
    """`start` abre la app en su propia ventana y desligada de Core (cerrar Core no la cierra)."""
    if command and command[0].lower().endswith((".bat", ".cmd")):
        # `start` abre un .bat con `cmd /K` y la consola se queda abierta y vacía al acabar
        command = ["cmd", "/c", *command]
    subprocess.Popen(["cmd", "/c", "start", "", *command], cwd=cwd, env=env,
                     creationflags=subprocess.CREATE_NO_WINDOW)


def _principal_of(app: Dict[str, Any]) -> str:
    return app.get("principal", app["id"])


@router.get("")
async def list_apps(flows: FlowsRepository = Depends(get_flows_repo)):
    result = await run_in_threadpool(statuses)
    priorities, senders = flows.priorities(), set(flows.broker_principals())
    principals = {a["id"]: _principal_of(a) for a in load_catalog()}
    for app in result["apps"]:
        principal = principals.get(app["id"], app["id"])
        # Sólo tiene prioridad quien manda trabajo al Broker; None = sin fijar (100 del Broker)
        app["broker_client"] = principal in senders
        app["priority"] = priorities.get(principal)
    return result


class PriorityRequest(BaseModel):
    priority: Optional[int] = Field(None, ge=0, le=1000)


@router.put("/{app_id}/priority")
def set_app_priority(app_id: str, body: PriorityRequest, request: Request,
                     flows: FlowsRepository = Depends(get_flows_repo)):
    """El director decide quién pasa antes en la cola del Broker (Client_API §5.1.1)."""
    _director_only(request)
    app = _catalog_entry(app_id)
    principal = _principal_of(app)
    if principal not in flows.broker_principals():
        raise HTTPException(status_code=400, detail=f"{app.get('name', app_id)} no manda trabajo al AI Broker.")
    flows.set_priority(principal, body.priority)
    record_safely(flows, flow_id=f"prioridad_{principal}_{int(time.time())}", kind="request", source="core",
                  target=principal, summary=f"prioridad {body.priority if body.priority is not None else 'por defecto'}",
                  details={"priority": body.priority, "set_by": "monitor"})
    return {"id": app_id, "principal": principal, "priority": body.priority}


def _director_only(request: Request) -> None:
    """Arrancar o parar apps es cosa del director: el token de una app no gobierna a las demás."""
    grant = getattr(request.state, "token_grant", None)
    if grant is not None and grant.principal:
        raise HTTPException(status_code=403, detail="Sólo el token del director (AI_OS_API_TOKEN) arranca o para apps.")
    if grant is None and (request.client is None or request.client.host not in ("127.0.0.1", "::1", "testclient")):
        raise HTTPException(status_code=403, detail="Sin token, sólo se arrancan o paran apps desde este mismo equipo.")


def _catalog_entry(app_id: str) -> Dict[str, Any]:
    app = next((a for a in load_catalog() if a["id"] == app_id), None)
    if app is None:
        raise HTTPException(status_code=404, detail=f"'{app_id}' no está en el catálogo de apps.")
    return app


def _kill(pids: List[int]) -> None:
    """Cierra cada proceso con su árbol: la consola del .bat, el python y sus hijos."""
    for pid in pids:
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True,
                       creationflags=subprocess.CREATE_NO_WINDOW)


@router.post("/{app_id}/stop", status_code=202)
async def stop_app(app_id: str, request: Request, force: bool = Query(False),
                   flows: FlowsRepository = Depends(get_flows_repo)):
    _director_only(request)
    app = _catalog_entry(app_id)
    if app.get("kind") == "remote" or not _marks(app):
        raise HTTPException(status_code=400, detail=f"{app.get('name', app_id)} no se para desde aquí. {app.get('note', '')}".strip())
    _process_cache["at"] = 0.0
    state = next(s for s in (await run_in_threadpool(statuses))["apps"] if s["id"] == app_id)
    if state["needed_by"] and not force:
        raise HTTPException(status_code=409, detail=f"{', '.join(state['needed_by'])} depende de {state['name']}: confirma para pararla igualmente.")
    own = {os.getpid(), os.getppid()}  # Core nunca se cierra a sí mismo
    pids = [pid for pid, line in await run_in_threadpool(_processes)
            if pid not in own and any(m in line for m in _marks(app))]
    if not pids:
        raise HTTPException(status_code=409, detail=f"{state['name']} no está en marcha.")
    await run_in_threadpool(_kill, pids)
    _process_cache["at"] = 0.0
    record_safely(flows, flow_id=f"parada_{app_id}_{int(time.time())}", kind="request", source="core",
                  target=app_id, summary="parada", details={"stopped_by": "monitor", "processes": len(pids)})
    return {"id": app_id, "status": "stopping", "processes": len(pids)}


@router.post("/{app_id}/start", status_code=202)
async def start_app(app_id: str, request: Request, flows: FlowsRepository = Depends(get_flows_repo)):
    _director_only(request)
    app = _catalog_entry(app_id)
    if app.get("kind") == "remote" or not app.get("start"):
        raise HTTPException(status_code=400, detail=f"{app.get('name', app_id)} no se arranca desde aquí. {app.get('note', '')}".strip())
    state = next(s for s in (await run_in_threadpool(statuses))["apps"] if s["id"] == app_id)
    if state["running"]:
        raise HTTPException(status_code=409, detail=f"{state['name']} ya está en marcha.")
    if state["blocked_by"]:
        raise HTTPException(status_code=409, detail=f"Antes hay que arrancar: {', '.join(state['blocked_by'])}.")
    core_url = str(request.base_url).rstrip("/")
    token = _token_for(app.get("principal", app_id))
    env = dict(os.environ)
    # La app arrancada desde aquí queda conectada a este Core con su propio token
    for key, value in (app.get("env") or {}).items():
        env[key] = str(value).replace("{core_url}", core_url).replace("{token}", token)
    try:
        await run_in_threadpool(_spawn, list(app["start"]), app.get("cwd"), env)
    except OSError as exc:
        raise HTTPException(status_code=500, detail=f"No se pudo lanzar {state['name']}: {exc}") from exc
    _process_cache["at"] = 0.0
    record_safely(flows, flow_id=f"arranque_{app_id}_{int(time.time())}", kind="request", source="core",
                  target=app_id, summary="arranque", details={"launched_by": "monitor"})
    return {"id": app_id, "status": "starting", "warnings": state["warnings"]}
