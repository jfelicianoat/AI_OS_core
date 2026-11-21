"""Tokens de cliente del AI Broker que Core emite para cada app (contrato 2.12, §3.2).

El token de administración del Broker lo abre todo y rota en cada arranque. Una app que
solo manda trabajo necesita menos: un token de cliente, que solo abre las rutas de trabajo
y solo sobre lo que creó esa app, y que sobrevive a los reinicios del Broker.

Core los emite con el token de administración que publica el runner de Agora, uno por
principal (el nombre en el Broker es el principal), y los guarda junto a su base para no
emitir otro en cada arranque. Antes de entregar uno guardado lo comprueba con
`GET /api/v1/auth/check`: si el operador lo revocó, emite otro. Si no puede emitir
(Broker antiguo, sin red, sin token de administración), quien llama decide qué hacer.

`AI_OS_BROKER_URL` fija la URL del Broker; `off` apaga todo esto. Por defecto sale de la
entrada `ai_broker` del catálogo de apps.
"""

import json
import os
import ssl
import threading
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from ai_os_core.config import settings

_lock = threading.Lock()
_DEFAULT_CA = r"C:\Agora\pki-broker\ca.crt"
_TIMEOUT_S = 8


class BrokerUnreachable(Exception):
    """No se pudo hablar con el Broker (red, TLS o respuesta ilegible)."""


def broker_url() -> Optional[str]:
    custom = os.getenv("AI_OS_BROKER_URL")
    if custom is not None:
        custom = custom.strip().rstrip("/")
        return None if custom.lower() in ("", "off", "false") else custom
    path = Path(os.getenv("AI_OS_APPS_FILE") or Path(__file__).resolve().parents[2] / "config" / "apps.json")
    try:
        apps = json.loads(path.read_text(encoding="utf-8")).get("apps", [])
    except (OSError, ValueError, AttributeError):
        return None
    for app in apps:
        health = str(app.get("health") or "") if isinstance(app, dict) and app.get("id") == "ai_broker" else ""
        if health.endswith("/health"):
            return health[: -len("/health")]
    return None


def _ssl_context() -> ssl.SSLContext:
    # La CA del Broker solo para hablar con él, igual que las apps (nunca SSL_CERT_FILE global)
    context = ssl.create_default_context()
    ca = os.getenv("AI_BROKER_CA_CERT") or _DEFAULT_CA
    if os.path.isfile(ca):
        context.load_verify_locations(ca)
    return context


def _call(method: str, url: str, token: str, body: Optional[dict] = None) -> tuple:
    """(estado, json) de una llamada al Broker; BrokerUnreachable si no hay respuesta HTTP."""
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(url, data=data, method=method, headers={
        "X-Admin-Token": token, "Content-Type": "application/json", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=_TIMEOUT_S, context=_ssl_context()) as response:
            status, raw = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, raw = error.code, error.read()
    except (OSError, ValueError) as error:
        raise BrokerUnreachable(str(error)) from error
    try:
        return status, (json.loads(raw) if raw else {})
    except ValueError as error:
        raise BrokerUnreachable(f"respuesta no JSON ({status})") from error


def _store_path() -> Path:
    return Path(settings.db_path).parent / "broker_client_tokens.json"


def _load() -> dict:
    try:
        data = json.loads(_store_path().read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: dict) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _still_valid(base: str, token: str) -> bool:
    """True si el Broker lo acepta como token de cliente; sin red se da por bueno (no se sabe)."""
    try:
        status, body = _call("GET", f"{base}/api/v1/auth/check", token)
    except BrokerUnreachable:
        return True
    return status == 200 and isinstance(body, dict) and body.get("scope") == "client"


def _mint(base: str, admin_token: str, name: str) -> Optional[str]:
    tokens_url = f"{base}/api/v1/admin/client-tokens"
    status, body = _call("POST", tokens_url, admin_token, {"name": name})
    if status == 409:
        # Ya hay uno activo con ese nombre y Core no tiene su valor (se perdió el fichero o
        # lo revocó y volvió a emitir otro el operador): se revoca y se emite de nuevo.
        status, listing = _call("GET", tokens_url, admin_token)
        items = listing if isinstance(listing, list) else (listing or {}).get("tokens") or (listing or {}).get("items") or []
        for item in items if status == 200 else []:
            if isinstance(item, dict) and item.get("name") == name and item.get("active"):
                _call("DELETE", f"{tokens_url}/{item['id']}", admin_token)
        status, body = _call("POST", tokens_url, admin_token, {"name": name})
    token = body.get("token") if status == 201 and isinstance(body, dict) else None
    return token if isinstance(token, str) and token else None


def client_token_for(principal: str, admin_token: Optional[str]) -> Optional[str]:
    """El token de cliente de `principal`, emitiéndolo si hace falta; None si no se puede."""
    base = broker_url()
    if base is None:
        return None
    with _lock:
        stored = _load()
        token = stored.get(principal)
        if token and _still_valid(base, token):
            return token
        if not admin_token:
            return None
        try:
            token = _mint(base, admin_token, principal)
        except BrokerUnreachable:
            return None
        if token:
            stored[principal] = token
            _save(stored)
        return token
