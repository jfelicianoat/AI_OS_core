"""Repositorio SQLite de los pasos de flujo que pinta el monitor (/monitor).
Comentarios en español.
"""

import json
from typing import Any, Dict, List, Optional
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.contracts import utc_now_iso


def _row(row) -> Dict[str, Any]:
    return {
        "id": row["id"], "flow_id": row["flow_id"], "at": row["at"], "kind": row["kind"],
        "source": row["source"], "target": row["target"], "summary": row["summary"],
        "details": json.loads(row["details_json"]),
    }


class FlowsRepository:
    """Registro append-only de pasos; el id autoincremental es el cursor del stream."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

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

    def flow(self, flow_id: str) -> List[Dict[str, Any]]:
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT * FROM flow_events WHERE flow_id = ? ORDER BY id ASC;", (flow_id,)).fetchall()
            return [_row(r) for r in rows]
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

    def policy_principals(self) -> List[str]:
        """Apps gobernadas por Core: el prefijo de los ámbitos `<app>:<destino>` de sus políticas."""
        conn = self.db_manager.get_connection()
        try:
            rows = conn.execute("SELECT DISTINCT scope FROM policies;").fetchall()
            return sorted({r["scope"].split(":", 1)[0] for r in rows if ":" in r["scope"]})
        finally:
            conn.close()
