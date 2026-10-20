"""Conexión automática de las apps con Core: a ninguna app hay que pegarle un token.

Core genera una sola vez un token por app (y el del director) y lo deja, junto con su URL,
en `%LOCALAPPDATA%\\AIOSCore\\conexion\\<principal>.json`. Las apps de este equipo lo leen
de ahí si no se lo pasa el lanzador por variables. La carpeta está en el perfil del
usuario: la leen él y sus programas, igual que sus variables de entorno.

Un token fijado a mano en AI_OS_API_TOKEN(S) manda sobre el generado y se copia al fichero.
`AI_OS_AUTO_TOKENS=false` lo desactiva (los tests lo hacen para no escribir en el perfil).
"""

import json
import os
import secrets
from pathlib import Path
from typing import Dict

DIRECTOR = "director"
# Los principals del ecosistema (los de scripts/sembrar_ecosistema.py)
PRINCIPALS = (
    "agora", "gestion_tareas", "athena", "chatygpt", "knowledge_orchestrator",
    "local_ai_lab", "model_drift", "trading_ai",
)


def auto_enabled() -> bool:
    return os.getenv("AI_OS_AUTO_TOKENS", "true").strip().lower() != "false"


def connect_dir() -> Path:
    custom = os.getenv("AI_OS_CONNECT_DIR", "").strip()
    if custom:
        return Path(custom)
    base = os.getenv("LOCALAPPDATA") or str(Path.home() / ".ai_os_core")
    return Path(base) / "AIOSCore" / "conexion"


def _read_token(path: Path) -> str:
    try:
        return str(json.loads(path.read_text(encoding="utf-8")).get("token") or "").strip()
    except (OSError, ValueError, AttributeError):
        return ""


def _write(path: Path, content: dict) -> None:
    text = json.dumps(content, indent=2, ensure_ascii=False)
    try:
        if path.read_text(encoding="utf-8") == text:
            return
    except OSError:
        pass
    tmp = path.with_suffix(".tmp")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)  # una app que lee a la vez ve el fichero viejo o el nuevo, nunca a medias


def provision(fixed: Dict[str, str], port: int) -> Dict[str, str]:
    """principal -> token para el director y cada app; crea los que falten y los publica.

    `fixed` son los tokens de las variables de entorno (el del director bajo DIRECTOR).
    """
    folder = connect_dir()
    folder.mkdir(parents=True, exist_ok=True)
    result = {}
    for principal in (DIRECTOR, *PRINCIPALS):
        path = folder / f"{principal}.json"
        token = fixed.get(principal) or _read_token(path) or secrets.token_urlsafe(32)
        _write(path, {"principal": principal, "core_url": f"http://127.0.0.1:{port}", "token": token})
        result[principal] = token
    return result
