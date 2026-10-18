"""Motor de Policies y evaluación ternaria para AI OS Core.
Alineado con Normativa 0.6.1 (§3) y casos críticos C08, C18, C19, C20.
Comentarios en español.
"""

from enum import Enum
from dataclasses import dataclass, field, asdict
from typing import Any, Optional
from .contracts import utc_now_iso


class TernaryResult(str, Enum):
    """Lógica ternaria requerida por la normativa."""
    TRUE = "TRUE"
    FALSE = "FALSE"
    UNKNOWN = "UNKNOWN"


class ConditionMode(str, Enum):
    """Modo de combinación de condiciones en una Policy."""
    ALL = "all"
    ANY = "any"


class AuthorizationDecision(str, Enum):
    """Resultado de autorización con precedencia estricta:
    DENY > REQUIRE_APPROVAL > INDETERMINATE > ALLOW
    """
    DENY = "DENY"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    INDETERMINATE = "INDETERMINATE"
    ALLOW = "ALLOW"


# Mapa de precedencia numérica (a menor número, mayor precedencia)
DECISION_PRECEDENCE = {
    AuthorizationDecision.DENY: 1,
    AuthorizationDecision.REQUIRE_APPROVAL: 2,
    AuthorizationDecision.INDETERMINATE: 3,
    AuthorizationDecision.ALLOW: 4,
}


# Operadores que el motor sabe evaluar; cualquier otro se rechaza al registrar la política
SUPPORTED_OPERATORS = frozenset({
    "exists", "equals", "not_equals",
    "greater_than", "less_than", "greater_or_equal", "less_or_equal",
    "in",
})


@dataclass
class PolicyCondition:
    """Condición individual evaluable contra un contexto."""
    field: str
    operator: str  # exists, equals, greater_than, less_than, in, not_equals
    value: Any = None

    def evaluate(self, context: dict[str, Any]) -> TernaryResult:
        """Evalúa la condición bajo semántica ternaria (Normativa 0.6.1 §3.2)."""
        present = self.field in context
        val = context.get(self.field) if present else None

        if self.operator == "exists":
            # Presente incluso null -> TRUE; ausente -> FALSE
            return TernaryResult.TRUE if present else TernaryResult.FALSE

        if self.operator == "equals":
            if self.value is None:
                # equals(field, null): presente null -> TRUE; presente no-null -> FALSE; ausente -> UNKNOWN
                if not present:
                    return TernaryResult.UNKNOWN
                return TernaryResult.TRUE if val is None else TernaryResult.FALSE
            if not present or val is None:
                return TernaryResult.UNKNOWN
            return TernaryResult.TRUE if val == self.value else TernaryResult.FALSE

        if self.operator == "not_equals":
            if not present or val is None:
                return TernaryResult.UNKNOWN
            return TernaryResult.TRUE if val != self.value else TernaryResult.FALSE

        if self.operator in ("greater_than", "less_than", "greater_or_equal", "less_or_equal"):
            # Comparación con null o ausente genera UNKNOWN
            if not present or val is None:
                return TernaryResult.UNKNOWN
            try:
                if self.operator == "greater_than":
                    return TernaryResult.TRUE if val > self.value else TernaryResult.FALSE
                if self.operator == "less_than":
                    return TernaryResult.TRUE if val < self.value else TernaryResult.FALSE
                if self.operator == "greater_or_equal":
                    return TernaryResult.TRUE if val >= self.value else TernaryResult.FALSE
                if self.operator == "less_or_equal":
                    return TernaryResult.TRUE if val <= self.value else TernaryResult.FALSE
            except TypeError:
                return TernaryResult.UNKNOWN

        if self.operator == "in":
            if not present or val is None or not isinstance(self.value, (list, tuple, set)):
                return TernaryResult.UNKNOWN
            return TernaryResult.TRUE if val in self.value else TernaryResult.FALSE

        # Operador no soportado -> considerado condición desconocida/inválida
        return TernaryResult.UNKNOWN


@dataclass
class Policy:
    """Definición canónica de una política en AI OS Core."""
    policy_id: str
    policy_key: str
    scope: str
    decision_if_matched: AuthorizationDecision
    conditions: list[PolicyCondition] = field(default_factory=list)
    condition_mode: ConditionMode = ConditionMode.ALL
    unconditional: bool = False
    enabled: bool = True
    revision: int = 1
    constraints: dict[str, Any] = field(default_factory=dict)
    obligations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=utc_now_iso)

    def validate_integrity(self) -> None:
        """Valida las reglas de integridad de la política (§3.1)."""
        if len(self.conditions) == 0 and not self.unconditional:
            raise ValueError("conditions=[] sólo es válido si unconditional=True")
        if self.unconditional and len(self.conditions) > 0:
            raise ValueError("unconditional=True con condiciones no vacías es inválido")
        for cond in self.conditions:
            if cond.operator not in SUPPORTED_OPERATORS:
                raise ValueError(
                    f"Operador '{cond.operator}' no soportado. Válidos: {sorted(SUPPORTED_OPERATORS)}"
                )
            if cond.operator == "in" and not isinstance(cond.value, (list, tuple, set)):
                raise ValueError(f"El operador 'in' de la condición sobre '{cond.field}' exige una lista como value.")

    def evaluate(self, context: dict[str, Any]) -> TernaryResult:
        """Evalúa las condiciones de la política según el modo (§3)."""
        self.validate_integrity()
        if self.unconditional:
            return TernaryResult.TRUE

        results = [cond.evaluate(context) for cond in self.conditions]

        if self.condition_mode == ConditionMode.ALL:
            # ALL: algún FALSE -> FALSE; sin FALSE y algún UNKNOWN -> UNKNOWN; todos TRUE -> TRUE
            if any(r == TernaryResult.FALSE for r in results):
                return TernaryResult.FALSE
            if any(r == TernaryResult.UNKNOWN for r in results):
                return TernaryResult.UNKNOWN
            return TernaryResult.TRUE

        if self.condition_mode == ConditionMode.ANY:
            # ANY: algún TRUE -> TRUE; sin TRUE y algún UNKNOWN -> UNKNOWN; todos FALSE -> FALSE
            if any(r == TernaryResult.TRUE for r in results):
                return TernaryResult.TRUE
            if any(r == TernaryResult.UNKNOWN for r in results):
                return TernaryResult.UNKNOWN
            return TernaryResult.FALSE

        return TernaryResult.UNKNOWN


@dataclass
class PolicyDecision:
    """Resultado formal consolidado de la evaluación de políticas."""
    authorization: AuthorizationDecision
    constraints: dict[str, Any] = field(default_factory=dict)
    obligations: list[str] = field(default_factory=list)
    matched_policy_refs: list[str] = field(default_factory=list)
    unknown_inputs: list[str] = field(default_factory=list)
    executable: bool = True
    trace_id: Optional[str] = None  # DecisionTrace del Core que respalda esta decisión

    def to_dict(self) -> dict[str, Any]:
        """Serializa a diccionario."""
        res = asdict(self)
        res["authorization"] = self.authorization.value
        return res
