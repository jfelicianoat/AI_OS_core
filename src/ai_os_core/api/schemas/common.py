"""Esquemas DTO base y de paginación estable.
Comentarios en español.
"""

from typing import Generic, TypeVar, List, Optional, Any, Dict
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginationParams(BaseModel):
    """Parámetros de paginación determinista."""
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


class PaginatedResponse(BaseModel, Generic[T]):
    """Respuesta paginada estándar."""
    items: List[T]
    total_returned: int
    offset: int
    limit: int


# DTOs para Goals
class CreateGoalRequest(BaseModel):
    title: str = Field(..., min_length=1)
    description: str
    owner_service: str = "ai_os_core"
    parent_goal_id: Optional[str] = None
    goal_id: Optional[str] = None


class UpdateGoalStatusRequest(BaseModel):
    status: str
    principal_id: str = "system"


class CreateObjectiveRequest(BaseModel):
    goal_id: str
    title: str = Field(..., min_length=1)
    description: str = ""
    objective_id: Optional[str] = None


# DTOs para Registro de Servicios y Capacidades
class ServiceRegistrationRequest(BaseModel):
    service_id: str
    name: str
    base_url: str
    version: str = "1.0.0"
    health_status: str = "healthy"
    capabilities: List[str] = []
    metadata: Dict[str, Any] = {}


class CapabilityRegistrationRequest(BaseModel):
    capability_id: str
    name: str
    description: str
    provider_service_id: str
    version: str = "1.0.0"
    schema_version: str = "1.0"
    is_available: bool = True
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}


# DTOs para Eventos
class EventIngestRequest(BaseModel):
    event_id: str
    producer_id: str
    stream_id: str
    stream_epoch: int
    source_sequence: int
    event_type: str  # full_state, delta, audit, notification
    resource_id: str
    resource_type: str
    revision: int
    payload: Dict[str, Any]
    state_digest: Optional[str] = None


class EventIngestResponse(BaseModel):
    event_id: str
    accepted_in_canonical_projection: bool
    quarantine: bool
    duplicate: bool = False
    reason: Optional[str] = None


# DTOs para Policies
class PolicyEvaluateRequest(BaseModel):
    scope: str
    context: Dict[str, Any]
    principal_id: str = "system"
    resource_id: Optional[str] = None


class PolicyConditionDTO(BaseModel):
    field: str
    operator: str
    value: Any = None


class CreatePolicyRequest(BaseModel):
    policy_id: str
    policy_key: str
    scope: str
    decision_if_matched: str
    conditions: List[PolicyConditionDTO] = []
    condition_mode: str = "all"
    unconditional: bool = False
    enabled: bool = True
    revision: int = 1
    constraints: Dict[str, Any] = {}
    obligations: List[str] = []


# DTOs para Approvals
class CreateApprovalRequest(BaseModel):
    authorization_id: str
    scope: str
    max_uses: int = Field(default=1, ge=1)
    expires_at: Optional[str] = None
    expected_digest: Optional[str] = None
    granted_by: str = "human"


class CommitApprovalUseRequest(BaseModel):
    use_id: str
    authorization_id: str
    operation_id: str
    operation_digest: str


# DTOs para Restore
class OperationStatusQueryRequest(BaseModel):
    operation_id: str
    target_service_id: str


class OperationReceiptDTO(BaseModel):
    operation_id: str
    receiver_service: str
    status: str
    result_digest: Optional[str] = None
    evidence: Dict[str, Any] = {}
    recommended_action: str
