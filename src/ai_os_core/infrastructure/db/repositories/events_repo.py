"""Repositorio SQLite para Eventos, ReplayCursor y Cuarentena (C02, C03, C05).
Comentarios en español.
"""

import json
import sqlite3
from typing import Optional, List, Tuple
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.events import EventEnvelope, EventType, ReplayCursor, ReplayGap
from ai_os_core.domain.contracts import utc_now_iso
from ai_os_core.domain.errors import ConflictError


# Prefijo del motivo devuelto cuando se reconoce una reentrega del mismo evento
DUPLICATE_EVENT_REASON = "DUPLICATE_EVENT"
REPLAY_GAP_REASON = "REPLAY_GAP"
STALE_EPOCH_REASON = "STALE_EPOCH"
CONTRADICTORY_REASON = "Contradictory full_state same revision with different state_digest"
CONSUMER_ID = "core_inbox"


class EventsRepository:
    """Gestiona el almacenamiento durable de eventos, detección de huecos de secuencia y proyecciones canónicas."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def ingest_event(self, event: EventEnvelope) -> Tuple[bool, Optional[str]]:
        """Ingesta un evento garantizando semántica transaccional, detección de huecos y reglas de revisión.
        Devuelve (success, quarantine_or_gap_reason).
        """
        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()

            # 0. Reentrega del mismo evento (entrega al-menos-una-vez): se reconoce
            # sin reprocesar. El mismo event_id con otra identidad de flujo, o un
            # hueco de secuencia ya ocupado por otro evento, es un conflicto.
            cursor.execute(
                "SELECT producer_id, stream_id, stream_epoch, source_sequence, quarantine, quarantine_reason, "
                "event_type, resource_id, revision, payload_json, state_digest "
                "FROM events WHERE event_id = ?;",
                (event.event_id,)
            )
            previous = cursor.fetchone()
            if previous:
                same_slot = (
                    previous["producer_id"] == event.producer_id
                    and previous["stream_id"] == event.stream_id
                    and previous["stream_epoch"] == event.stream_epoch
                    and previous["source_sequence"] == event.source_sequence
                )
                if not same_slot:
                    raise ConflictError(
                        f"El event_id '{event.event_id}' ya existe con otra identidad de flujo/secuencia."
                    )
                same_content = (
                    previous["event_type"] == event.event_type.value
                    and previous["resource_id"] == event.resource_id
                    and previous["revision"] == event.revision
                    and previous["state_digest"] == event.state_digest
                    and json.loads(previous["payload_json"]) == event.payload
                )
                if not same_content:
                    # Reutilizar un event_id con otro contenido no es una reentrega: es divergencia
                    raise ConflictError(f"El event_id '{event.event_id}' ya existe con otro contenido.")
                event.quarantine = bool(previous["quarantine"])
                event.quarantine_reason = previous["quarantine_reason"]
                return not event.quarantine, f"{DUPLICATE_EVENT_REASON}: evento ya recibido; no se reprocesa."

            cursor.execute(
                "SELECT event_id FROM events WHERE producer_id = ? AND stream_id = ? AND stream_epoch = ? AND source_sequence = ?;",
                (event.producer_id, event.stream_id, event.stream_epoch, event.source_sequence)
            )
            occupied = cursor.fetchone()
            if occupied:
                raise ConflictError(
                    f"La secuencia {event.source_sequence} del flujo '{event.producer_id}/{event.stream_id}' "
                    f"(epoch {event.stream_epoch}) ya la ocupa el evento '{occupied['event_id']}'."
                )

            # 1. Eventos de un epoch anterior al vigente: sólo auditoría (§6). Se guardan
            # pero no tocan la proyección ni el cursor.
            cursor.execute(
                "SELECT MAX(stream_epoch) FROM events WHERE producer_id = ? AND stream_id = ?;",
                (event.producer_id, event.stream_id)
            )
            max_epoch = cursor.fetchone()[0]
            if max_epoch is not None and event.stream_epoch < max_epoch:
                event.quarantine = True
                event.quarantine_reason = (
                    f"{STALE_EPOCH_REASON}: epoch {event.stream_epoch} anterior al vigente {max_epoch}; sólo auditoría."
                )
            else:
                # 2. Caso C05: la secuencia esperada sale del cursor, que sólo avanza con
                # eventos aplicados en orden. Contar los de cuarentena (como antes) tapaba
                # el hueco: el evento que lo causó se perdía y el siguiente entraba sin él.
                last_seq = self._cursor(cursor, event)
                if event.source_sequence > last_seq + 1:
                    cursor.execute(
                        """
                        INSERT INTO replay_gaps (producer_id, stream_id, stream_epoch, expected_sequence, received_sequence, detected_at, resolved)
                        VALUES (?, ?, ?, ?, ?, ?, 0);
                        """,
                        (event.producer_id, event.stream_id, event.stream_epoch, last_seq + 1, event.source_sequence, utc_now_iso())
                    )
                    event.quarantine = True
                    event.quarantine_reason = (
                        f"{REPLAY_GAP_REASON} detectado: se esperaba secuencia {last_seq + 1} pero llegó {event.source_sequence}."
                    )
                elif self._contradicts(cursor, event.event_type.value, event.resource_id, event.revision, event.state_digest):
                    # 3. Caso C03: misma revisión full_state con otro digest
                    event.quarantine = True
                    event.quarantine_reason = CONTRADICTORY_REASON

            # 4. Insertar el evento (C02: un full_state de revisión menor se guarda, pero la
            # proyección canónica toma siempre la revisión máxima y no retrocede)
            cursor.execute(
                """
                INSERT INTO events (
                    event_id, producer_id, stream_id, stream_epoch, source_sequence,
                    event_type, resource_id, resource_type, revision, payload_json,
                    state_digest, quarantine, quarantine_reason, created_at, received_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
                """,
                (
                    event.event_id,
                    event.producer_id,
                    event.stream_id,
                    event.stream_epoch,
                    event.source_sequence,
                    event.event_type.value,
                    event.resource_id,
                    event.resource_type,
                    event.revision,
                    json.dumps(event.payload),
                    event.state_digest,
                    1 if event.quarantine else 0,
                    event.quarantine_reason,
                    event.created_at,
                    event.received_at
                )
            )

            # 5. Un evento en orden (aunque se retenga por contradicción) avanza el cursor y
            # reanuda los que esperaban en cuarentena por el hueco que acaba de cerrar.
            in_order = not (event.quarantine_reason or "").startswith((REPLAY_GAP_REASON, STALE_EPOCH_REASON))
            if in_order:
                self._advance_and_resume(cursor, event)

            return not event.quarantine, event.quarantine_reason

    @staticmethod
    def _cursor(cursor: sqlite3.Cursor, event: EventEnvelope) -> int:
        """Última secuencia aplicada en orden del flujo (0 si no hay ninguna)."""
        cursor.execute(
            "SELECT last_processed_sequence FROM replay_cursors "
            "WHERE consumer_id = ? AND producer_id = ? AND stream_id = ? AND stream_epoch = ?;",
            (CONSUMER_ID, event.producer_id, event.stream_id, event.stream_epoch)
        )
        row = cursor.fetchone()
        return row[0] if row else 0

    @staticmethod
    def _contradicts(cursor: sqlite3.Cursor, event_type: str, resource_id: str, revision: int, digest: Optional[str]) -> bool:
        """Caso C03: ya hay un full_state aplicado de esa revisión con otro state_digest."""
        if event_type != EventType.FULL_STATE.value:
            return False
        cursor.execute(
            "SELECT state_digest FROM events WHERE resource_id = ? AND revision = ? AND event_type = ? AND quarantine = 0;",
            (resource_id, revision, EventType.FULL_STATE.value)
        )
        existing = cursor.fetchone()
        return bool(existing and existing["state_digest"] != digest)

    def _advance_and_resume(self, cursor: sqlite3.Cursor, event: EventEnvelope) -> None:
        """Avanza el cursor y aplica, en orden, los eventos retenidos por REPLAY_GAP que ya encajan."""
        seq = event.source_sequence
        while True:
            cursor.execute(
                "SELECT event_id, event_type, resource_id, revision, state_digest FROM events "
                "WHERE producer_id = ? AND stream_id = ? AND stream_epoch = ? AND source_sequence = ? "
                "AND quarantine = 1 AND quarantine_reason LIKE ?;",
                (event.producer_id, event.stream_id, event.stream_epoch, seq + 1, f"{REPLAY_GAP_REASON}%")
            )
            pending = cursor.fetchone()
            if not pending:
                break
            seq += 1
            if self._contradicts(cursor, pending["event_type"], pending["resource_id"], pending["revision"], pending["state_digest"]):
                cursor.execute("UPDATE events SET quarantine_reason = ? WHERE event_id = ?;", (CONTRADICTORY_REASON, pending["event_id"]))
            else:
                cursor.execute("UPDATE events SET quarantine = 0, quarantine_reason = NULL WHERE event_id = ?;", (pending["event_id"],))
        cursor.execute(
            """
            INSERT INTO replay_cursors (consumer_id, producer_id, stream_id, stream_epoch, last_processed_sequence, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(consumer_id, producer_id, stream_id, stream_epoch) DO UPDATE SET
                last_processed_sequence = MAX(replay_cursors.last_processed_sequence, excluded.last_processed_sequence),
                updated_at = excluded.updated_at;
            """,
            (CONSUMER_ID, event.producer_id, event.stream_id, event.stream_epoch, seq, utc_now_iso())
        )
        # Un hueco queda resuelto cuando el cursor alcanza el evento que lo destapó
        cursor.execute(
            "UPDATE replay_gaps SET resolved = 1 WHERE producer_id = ? AND stream_id = ? AND stream_epoch = ? "
            "AND resolved = 0 AND received_sequence <= ?;",
            (event.producer_id, event.stream_id, event.stream_epoch, seq)
        )

    def get_latest_canonical_state(self, resource_id: str) -> Optional[dict]:
        """Obtiene la proyección canónica vigente (solo full_state no en cuarentena con revisión máxima)."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT revision, payload_json, state_digest, created_at FROM events
                WHERE resource_id = ? AND event_type = ? AND quarantine = 0
                ORDER BY revision DESC, source_sequence DESC LIMIT 1;
                """,
                (resource_id, EventType.FULL_STATE.value)
            )
            row = cursor.fetchone()
            if not row:
                return None
            return {
                "resource_id": resource_id,
                "revision": row["revision"],
                "payload": json.loads(row["payload_json"]),
                "state_digest": row["state_digest"],
                "updated_at": row["created_at"]
            }
        finally:
            conn.close()

    def list_unresolved_gaps(self) -> List[ReplayGap]:
        """Lista todos los huecos de secuencia pendientes de reconciliación."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM replay_gaps WHERE resolved = 0 ORDER BY detected_at ASC;")
            rows = cursor.fetchall()
            return [
                ReplayGap(
                    producer_id=row["producer_id"],
                    stream_id=row["stream_id"],
                    stream_epoch=row["stream_epoch"],
                    expected_sequence=row["expected_sequence"],
                    received_sequence=row["received_sequence"],
                    detected_at=row["detected_at"],
                    resolved=bool(row["resolved"])
                )
                for row in rows
            ]
        finally:
            conn.close()

    def list_quarantined_events(self, limit: int = 50, offset: int = 0) -> List[dict]:
        """Lista los eventos retenidos en cuarentena (huecos y contradicciones) para su revisión."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT event_id, producer_id, stream_id, stream_epoch, source_sequence, event_type,
                       resource_id, revision, state_digest, quarantine_reason, received_at
                FROM events WHERE quarantine = 1
                ORDER BY received_at ASC, event_id ASC LIMIT ? OFFSET ?;
                """,
                (limit, offset)
            )
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
