# Matriz de conservación normativa 0.4 → 0.6

Esta matriz existe para impedir que una simplificación editorial elimine una decisión ya tomada sin declararlo.

| Regla previa | Estado 0.6 | Destino 0.6 |
|---|---|---|
| Default DENY sin permiso suficiente | Conservada | `INV-SEC-DEFAULT-DENY` |
| Techo efectivo de clasificación = intersección principal/Policy/destino/request | Conservada | `INV-SEC-CLASSIFICATION` |
| ServiceRegistration con allowlist y límites de red | Conservada | `INV-SEC-SERVICE-ENDPOINT` |
| No reenviar credenciales a redirect/destino no autorizado | Conservada | `INV-SEC-SERVICE-ENDPOINT` |
| Diferenciar schema/resource/service/capability/skill/policy/model revisions | Conservada | `INV-ID-LEGACY-BINDING` |
| Mantener IDs legacy y adapter_revision cuando no hay revisión nativa | Conservada | `INV-ID-LEGACY-BINDING` |
| Approval exact_action y scoped | Conservada | `INV-APPROVAL-EXACT-SCOPED` |
| ApprovalUse + Command/outbox atómicos | Conservada | sección 5 |
| Idempotency record y operación Core atómicos | Conservada | `INV-IDEMPOTENCY-ATOMIC` |
| Context: retrieved_at y validity_at_use | Conservada | `INV-CONTEXT-VALIDITY` |
| Distinguir usable_until de historical retention | Conservada | `INV-CONTEXT-VALIDITY` |
| Exclusiones consumer-safe vs privileged-audit | Conservada | `INV-CONTEXT-VALIDITY` |
| Task dependencies bloqueantes acíclicas | Conservada | `INV-TASK-DAG` |
| Artifact authority/producer/custodian distintos | Conservada | `INV-ARTIFACT-ROLES` |
| PlanningService pertenece al Core | Conservada | `INV-PLANNER-BOUNDARY` |
| Core no crea Jobs directamente | Conservada | `INV-PLANNER-BOUNDARY` |
| Gates authorization→certification→admission antes de A0–A5 | Conservada | `INV-AUTONOMY-GATES` |
| Bloqueado no equivale a A0 | Conservada | `INV-AUTONOMY-GATES` |
| Sólo full_state actualiza proyección en M0–M2 | Conservada | sección 6 |
| Hard GPU reservation futura fuera del MVP | Conservada | sección 12 |
| ExecutionAdmission único | Sustituida deliberadamente | `WorkerAdmission` + `InferenceAdmission` |
| AIReservation en MVP | Retirada deliberadamente | forecast + admisión al ejecutar |
| Aplicación de deltas | Diferida explícitamente | fuera de M0–M2 |
| Planner automático | Diferido | M5 |
| Autonomía condicional completa | Diferida | M6; sólo mínimo normativo en sección 13 |

## Regla de mantenimiento

Una fila `Conservada` sólo puede eliminarse de una revisión posterior si:
1. existe una decisión explícita que la sustituye o retira;
2. la nueva revisión actualiza esta matriz;
3. el Acceptance Registry invalida consumidores afectados cuando proceda.
