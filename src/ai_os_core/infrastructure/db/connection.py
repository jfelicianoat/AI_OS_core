"""Gestor de conexión y durabilidad SQLite para AI OS Core.
Alineado con DECISION_SQLITE_DURABILITY y OS-1 (§20).
Comentarios en español.
"""

import sqlite3
import os
from pathlib import Path
from typing import Generator
from contextlib import contextmanager

from ai_os_core.config import settings


class DatabaseManager:
    """Administrador de conexiones SQLite con configuración obligatoria de durabilidad."""

    def __init__(self, db_path: str | None = None, synchronous: str | None = None, busy_timeout: int | None = None):
        raw_path = db_path or settings.db_path
        self.synchronous = synchronous or settings.sqlite_synchronous
        self.busy_timeout = busy_timeout or settings.sqlite_busy_timeout_ms
        self._anchor_conn = None
        self._is_memory = (raw_path == ":memory:" or "mode=memory" in raw_path)

        if raw_path == ":memory:":
            import uuid
            self.db_path = f"file:mem_{uuid.uuid4().hex}?mode=memory&cache=shared"
        else:
            self.db_path = raw_path

        if self._is_memory:
            self._anchor_conn = sqlite3.connect(self.db_path, uri=True, check_same_thread=False)
            cursor = self._anchor_conn.cursor()
            cursor.execute("PRAGMA foreign_keys = ON;")
            cursor.execute(f"PRAGMA busy_timeout = {self.busy_timeout};")
            cursor.close()

        self._ensure_dir()

    def _ensure_dir(self) -> None:
        """Asegura que el directorio de la base de datos exista si es una ruta en disco."""
        if not self._is_memory and not self.db_path.startswith("file:"):
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

    def get_connection(self) -> sqlite3.Connection:
        """Crea y configura una nueva conexión con pragmas normativos."""
        is_uri = self.db_path.startswith("file:")
        conn = sqlite3.connect(
            self.db_path,
            timeout=self.busy_timeout / 1000.0,
            check_same_thread=False,
            uri=is_uri
        )
        conn.row_factory = sqlite3.Row

        # Pragmas normativos obligatorios
        cursor = conn.cursor()
        cursor.execute("PRAGMA foreign_keys = ON;")
        if not self._is_memory:
            cursor.execute("PRAGMA journal_mode = WAL;")
            cursor.execute(f"PRAGMA synchronous = {self.synchronous};")
        cursor.execute(f"PRAGMA busy_timeout = {self.busy_timeout};")
        cursor.close()

        return conn

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager que maneja transacciones atómicas commit/rollback.

        Abre la transacción con BEGIN IMMEDIATE: el bloqueo de escritura se toma
        antes de la primera lectura. Con una transacción diferida, dos peticiones
        concurrentes leían el mismo saldo o el mismo número de usos y ambas
        escribían (C07 y C09 fallaban bajo carga real).
        """
        conn = self.get_connection()
        try:
            conn.execute("BEGIN IMMEDIATE;")
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()


# Instancia por defecto
db_manager = DatabaseManager()
