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
                "SELECT producer_id, stream_id, stream_epoch, source_sequence, quarantine, quarantine_reason "
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

            # 1. Comprobar secuencia previa para el flujo (producer_id, stream_id, stream_epoch)
            cursor.execute(
                """
                SELECT MAX(source_sequence) FROM events
                WHERE producer_id = ? AND stream_id = ? AND stream_epoch = ?;
                """,
                (event.producer_id, event.stream_id, event.stream_epoch)
            )
            row = cursor.fetchone()
            last_seq = row[0] if (row and row[0] is not None) else 0

            # Caso C05: Hueco de secuencia no recuperable (Replay Gap)
            if event.source_sequence > last_seq + 1:
                cursor.execute(
                    """
                    INSERT INTO replay_gaps (producer_id, stream_id, stream_epoch, expected_sequence, received_sequence, detected_at, resolved)
                    VALUES (?, ?, ?, ?, ?, ?, 0);
                    """,
                    (event.producer_id, event.stream_id, event.stream_epoch, last_seq + 1, event.source_sequence, utc_now_iso())
                )
                gap_reason = f"REPLAY_GAP detectado: se esperaba secuencia {last_seq + 1} pero llegó {event.source_sequence}."
                # Almacenar en cuarentena
                event.quarantine = True
                event.quarantine_reason = gap_reason

            # 2. Caso C03: Contradicción en misma revisión para full_state
            if event.event_type == EventType.FULL_STATE:
                cursor.execute(
                    """
                    SELECT state_digest FROM events
                    WHERE resource_id = ? AND revision = ? AND event_type = ? AND quarantine = 0;
                    """,
                    (event.resource_id, event.revision, EventType.FULL_STATE.value)
                )
                existing = cursor.fetchone()
                if existing and existing["state_digest"] != event.state_digest:
                    event.quarantine = True
                    event.quarantine_reason = "Contradictory full_state same revision with different state_digest"

            # 3. Caso C02: Late event - Comprobar si existe una revisión mayor en la proyección canónica
            cursor.execute(
                """
                SELECT MAX(revision) FROM events
                WHERE resource_id = ? AND event_type = ? AND quarantine = 0;
                """,
                (event.resource_id, EventType.FULL_STATE.value)
            )
            max_rev_row = cursor.fetchone()
            max_rev = max_rev_row[0] if (max_rev_row and max_rev_row[0] is not None) else 0

            is_late_event = False
            if event.event_type == EventType.FULL_STATE and event.revision < max_rev:
                # Se persiste el evento para auditoría, pero no debe revertir la proyección más reciente
                is_late_event = True

            # 4. Insertar el evento
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

            # 5. Actualizar el cursor si no está en cuarentena
            if not event.quarantine:
                cursor.execute(
                    """
                    INSERT INTO replay_cursors (consumer_id, producer_id, stream_id, stream_epoch, last_processed_sequence, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(consumer_id, producer_id, stream_id, stream_epoch) DO UPDATE SET
                        last_processed_sequence = MAX(replay_cursors.last_processed_sequence, excluded.last_processed_sequence),
                        updated_at = excluded.updated_at;
                    """,
                    ("core_inbox", event.producer_id, event.stream_id, event.stream_epoch, event.source_sequence, utc_now_iso())
                )

            return not event.quarantine, event.quarantine_reason

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
