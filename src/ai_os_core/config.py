"""Módulo de configuración para AI OS Core.
Comentado en español según normativa del proyecto.
"""

import os
from pathlib import Path
from dataclasses import dataclass, field

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field
    HAS_PYDANTIC_SETTINGS = True
except ImportError:
    HAS_PYDANTIC_SETTINGS = False


def _get_default_db_path() -> str:
    """Calcula la ruta predeterminada de la base de datos SQLite."""
    local_app_data = os.getenv("LOCALAPPDATA")
    if local_app_data:
        base_dir = Path(local_app_data) / "AIOSCore" / "data"
    else:
        base_dir = Path.home() / ".ai_os_core" / "data"
    return str(base_dir / "ai_os_core.db")


@dataclass
class Settings:
    """Configuración centralizada de la aplicación."""
    # Entorno y servidor
    env: str = field(default_factory=lambda: os.getenv("AI_OS_ENV", "development"))
    host: str = field(default_factory=lambda: os.getenv("AI_OS_HOST", "127.0.0.1"))
    port: int = field(default_factory=lambda: int(os.getenv("AI_OS_PORT", "8000")))

    # Base de datos SQLite y durabilidad
    db_path: str = field(default_factory=lambda: os.getenv("AI_OS_DB_PATH", _get_default_db_path()))
    sqlite_synchronous: str = field(default_factory=lambda: os.getenv("AI_OS_SQLITE_SYNCHRONOUS", "FULL"))
    sqlite_busy_timeout_ms: int = field(default_factory=lambda: int(os.getenv("AI_OS_SQLITE_TIMEOUT_MS", "5000")))

    # Seguridad y allowlist de endpoints
    # AI_OS_ALLOWED_HOSTS añade hosts separados por comas (p. ej. nombres DNS de la LAN)
    allowed_service_hosts: list[str] = field(default_factory=lambda: [
        "localhost",
        "127.0.0.1",
        "::1"
    ] + [h.strip() for h in os.getenv("AI_OS_ALLOWED_HOSTS", "").split(",") if h.strip()])
    allow_private_networks: bool = field(default_factory=lambda: os.getenv("AI_OS_ALLOW_PRIVATE_NETS", "true").lower() == "true")


# Instancia singleton accesible globalmente
settings = Settings()
