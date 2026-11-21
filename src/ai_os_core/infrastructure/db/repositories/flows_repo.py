"""Repositorio SQLite de los pasos de flujo que pinta el monitor (/monitor).
Comentarios en español.
"""

import json
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.contracts import utc_now_iso


def _row(row) -> Dict[str, Any]:
    return {
        "id": row["id"], "flow_id": row["flow_id"], "at": row["at"], "kind": row["kind"],
        "source": row["source"], "target": row["target"], "summary": row["summary"],
        "details": json.loads(row["details_json"]),
    }


#: Días que se guardan los pasos del monitor (sólo metadatos de tráfico; recibos y trazas no se tocan).
#: Con KO activo entran miles por día: en un mes la tabla llegó a 75 861 filas (36 MB). 0 = no podar.
def retention_days() -> int:
    try:
        return max(0, int(os.getenv("AI_OS_MONITOR_RETENTION_DAYS", "90")))
    except ValueError:
        return 90


_PRUNE_EVERY_S = 3600.0


class FlowsRepository:
    """Registro append-only de pasos; el id autoincremental es el cursor del stream."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager
        self._pruned_at = 0.0

    def prune(self, days: Optional[int] = None) -> int:
        """Borra los pasos de hace más de `days` días (por defecto, la retención configurada)."""
        days = retention_days() if days is None else days
        if days <= 0:
            return 0
        cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()
        with self.db_manager.transaction() as conn:
            return conn.execute("DELETE FROM flow_events WHERE at < ?;", (cutoff,)).rowcount

    def append(self, flow_id: str, kind: str, source: str, target: str,
               summary: str = "", details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        at = utc_now_iso()
        details = details or {}
        with self.db_manager.transaction() as conn:
            cur = conn.execute(
                "INSERT INTO flow_events (flow_id, at, kind, source, target, summary, details_json) "
                "VALUES (?, ?, ?, ?, ?, ?, ?);",
                (flow_id, at, kind, source, target, summary, json.dumps(details, sort_keys=True)),
            )
            new_id = cur.lastrowid
        if time.monotonic() - self._pruned_at > _PRUNE_EVERY_S:  # Core vive semanas: se poda en marcha
            self._pruned_at = time.monotonic()
            self.prune()
        return {"id": new_id, "flow_id": flow_id, "at": at, "kind": kind, "source": source,
                "target": target, "summary": summary, "details": details}

    def after(self, after_id: int, limit: int) -> List[Dict[str, Any]]:
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM flow_events WHERE id > ? ORDER BY id ASC LIMIT ?;", (after_id, limit)
            ).fetchall()
            return [_row(r) for r in rows]
        finally:
            conn.close()

    def tail(self, limit: int) -> List[Dict[str, Any]]:
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT * FROM flow_events ORDER BY id DESC LIMIT ?;", (limit,)).fetchall()
            return [_row(r) for r in reversed(rows)]
        finally:
            conn.close()

    def last_id(self) -> int:
        conn = self.db_manager.get_connection()
        try:
            return conn.execute("SELECT COALESCE(MAX(id), 0) FROM flow_events;").fetchone()[0]
        finally:
            conn.close()

    def flow(self, flow_id: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Pasos del flujo en orden; con `limit`, sólo los últimos (un flujo diario de KO pasa de 10 000)."""
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT * FROM flow_events WHERE flow_id = ? ORDER BY id DESC LIMIT ?;",
                                (flow_id, -1 if limit is None else limit)).fetchall()
            return [_row(r) for r in reversed(rows)]
        finally:
            conn.close()

    def count(self, flow_id: str) -> int:
        conn = self.db_manager.get_connection()
        try:
            return conn.execute("SELECT COUNT(*) FROM flow_events WHERE flow_id = ?;", (flow_id,)).fetchone()[0]
        finally:
            conn.close()

    def last(self, flow_id: str) -> Optional[Dict[str, Any]]:
        conn = self.db_manager.get_connection()
        try:
            row = conn.execute("SELECT * FROM flow_events WHERE flow_id = ? ORDER BY id DESC LIMIT 1;", (flow_id,)).fetchone()
            return _row(row) if row else None
        finally:
            conn.close()

    def participants(self) -> List[str]:
        """Apps vistas en algún flujo, como origen o destino."""
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT source AS app FROM flow_events UNION SELECT target FROM flow_events;").fetchall()
            return [r["app"] for r in rows]
        finally:
            conn.close()

    def broker_principals(self) -> List[str]:
        """Apps que mandan trabajo al Broker: las que tienen una política `<app>:broker`."""
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT DISTINCT scope FROM policies WHERE scope LIKE '%:broker';").fetchall()
            return sorted({r["scope"].split(":", 1)[0] for r in rows})
        finally:
            conn.close()

    def priorities(self) -> Dict[str, int]:
        """Prioridad en la cola del Broker que el director ha fijado a cada app."""
        conn = self.db_manager.get_connection()
        try:
            return {r["app"]: r["priority"] for r in conn.execute("SELECT app, priority FROM app_priorities;")}
        finally:
            conn.close()

    def set_priority(self, app: str, priority: Optional[int]) -> None:
        """`None` la borra: la app deja de mandarla y el Broker usa su 100 por defecto."""
        with self.db_manager.transaction() as conn:
            if priority is None:
                conn.execute("DELETE FROM app_priorities WHERE app = ?;", (app,))
            else:
                conn.execute(
                    "INSERT INTO app_priorities (app, priority, updated_at) VALUES (?, ?, ?) "
                    "ON CONFLICT(app) DO UPDATE SET priority = excluded.priority, updated_at = excluded.updated_at;",
                    (app, priority, utc_now_iso()),
                )

    def policy_principals(self) -> List[str]:
        """Apps gobernadas por Core: el prefijo de los ámbitos `<app>:<destino>` de sus políticas."""
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT DISTINCT scope FROM policies;").fetchall()
            return sorted({r["scope"].split(":", 1)[0] for r in rows if ":" in r["scope"]})
        finally:
            conn.close()
