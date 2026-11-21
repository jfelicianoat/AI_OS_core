"""Repositorio SQLite para Policies (M0-POLICY-BASE).
Comentarios en español.
"""

import json
from typing import Optional, List
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.domain.errors import ConflictError
from ai_os_core.domain.policies import (
    Policy,
    PolicyCondition,
    AuthorizationDecision,
    ConditionMode
)


class PoliciesRepository:
    """Gestiona la persistencia de definiciones de políticas."""

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def save_policy(self, policy: Policy) -> bool:
        """Persiste una política asegurando integridad de sus condiciones. True si es nueva.

        Reglas (spec 0.6.1 §3.3, auditoría 19-nov): un `policy_id` no cambia de `scope` ni de
        `policy_key` (antes se respondía «created» y no cambiaba nada); la revisión no retrocede;
        y por `(policy_key, scope)` sólo hay una política habilitada.
        """
        policy.validate_integrity()
        conditions_data = [
            {"field": c.field, "operator": c.operator, "value": c.value}
            for c in policy.conditions
        ]

        with self.db_manager.transaction() as conn:
            cursor = conn.cursor()
            current = cursor.execute("SELECT * FROM policies WHERE policy_id = ?;", (policy.policy_id,)).fetchone()
            if current:
                if (current["scope"], current["policy_key"]) != (policy.scope, policy.policy_key):
                    raise ConflictError(
                        f"La política '{policy.policy_id}' es '{current['policy_key']}' en '{current['scope']}': "
                        "no cambia de clave ni de ámbito; crea otra con otro policy_id."
                    )
                if policy.revision < current["revision"]:
                    raise ConflictError(
                        f"Revisión obsoleta {policy.revision} para '{policy.policy_id}' (actual {current['revision']})."
                    )
                if policy.revision == current["revision"]:
                    # Con la misma revisión sólo se habilita o deshabilita: si cambiara la decisión, una traza que
                    # cita '<id>@<rev>' pasaría a significar otra cosa (arbitraje O-3)
                    antes = self._row_to_policy(current)
                    contenido = lambda p: (p.decision_if_matched, p.condition_mode, p.unconditional,  # noqa: E731
                                           [(c.field, c.operator, c.value) for c in p.conditions],
                                           p.constraints, p.obligations)
                    if contenido(antes) != contenido(policy):
                        raise ConflictError(
                            f"La política '{policy.policy_id}' cambia de contenido sin subir la revisión "
                            f"(sigue en {current['revision']}): envía revision={current['revision'] + 1}."
                        )
            if policy.enabled:
                twin = cursor.execute(
                    "SELECT policy_id FROM policies WHERE policy_key = ? AND scope = ? AND enabled = 1 AND policy_id <> ?;",
                    (policy.policy_key, policy.scope, policy.policy_id),
                ).fetchone()
                if twin:
                    raise ConflictError(
                        f"Ya hay una política habilitada '{policy.policy_key}' en '{policy.scope}' ({twin['policy_id']}): "
                        "sube su revisión o deshabilítala antes."
                    )
            cursor.execute(
                """
                INSERT INTO policies (
                    policy_id, policy_key, scope, decision_if_matched, condition_mode,
                    conditions_json, unconditional, enabled, revision, constraints_json,
                    obligations_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(policy_id) DO UPDATE SET
                    decision_if_matched = excluded.decision_if_matched,
                    condition_mode = excluded.condition_mode,
                    conditions_json = excluded.conditions_json,
                    unconditional = excluded.unconditional,
                    enabled = excluded.enabled,
                    revision = excluded.revision,
                    constraints_json = excluded.constraints_json,
                    obligations_json = excluded.obligations_json;
                """,
                (
                    policy.policy_id,
                    policy.policy_key,
                    policy.scope,
                    policy.decision_if_matched.value,
                    policy.condition_mode.value,
                    json.dumps(conditions_data),
                    1 if policy.unconditional else 0,
                    1 if policy.enabled else 0,
                    policy.revision,
                    json.dumps(policy.constraints),
                    json.dumps(policy.obligations),
                    policy.created_at
                )
            )
            return current is None

    def list_active_policies_for_scope(self, scope: str) -> List[Policy]:
        """Obtiene las políticas habilitadas aplicables a un scope determinado."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT * FROM policies
                WHERE (scope = ? OR scope = '*') AND enabled = 1
                ORDER BY created_at ASC;
                """,
                (scope,)
            )
            return [self._row_to_policy(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    def list_policies(self, scope: Optional[str] = None) -> List[Policy]:
        """Lista todas las políticas (habilitadas o no), opcionalmente de un scope exacto."""
        conn = self.db_manager.get_connection()
        try:
            cursor = conn.cursor()
            if scope:
                cursor.execute("SELECT * FROM policies WHERE scope = ? ORDER BY created_at ASC, policy_id ASC;", (scope,))
            else:
                cursor.execute("SELECT * FROM policies ORDER BY scope ASC, created_at ASC, policy_id ASC;")
            return [self._row_to_policy(row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def _row_to_policy(row) -> Policy:
        """Reconstruye una Policy desde su fila."""
        conditions = [
            PolicyCondition(field=c["field"], operator=c["operator"], value=c["value"])
            for c in json.loads(row["conditions_json"])
        ]
        return Policy(
            policy_id=row["policy_id"],
            policy_key=row["policy_key"],
            scope=row["scope"],
            decision_if_matched=AuthorizationDecision(row["decision_if_matched"]),
            conditions=conditions,
            condition_mode=ConditionMode(row["condition_mode"]),
            unconditional=bool(row["unconditional"]),
            enabled=bool(row["enabled"]),
            revision=row["revision"],
            constraints=json.loads(row["constraints_json"]),
            obligations=json.loads(row["obligations_json"]),
            created_at=row["created_at"]
        )
