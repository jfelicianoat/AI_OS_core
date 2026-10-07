# Reglas globales

Baseline obligatoria: Spec 0.6.1, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`.

Antes de modificar un repositorio, el agente debe inspeccionar su estado real, registrar repo/ref/commit, localizar APIs/contratos existentes y resumir `CURRENT_STATE_FINDINGS`.

Invariantes que no pueden degradarse:
- default DENY sin permiso suficiente;
- classification ceiling solicitado no concede autorización;
- ServiceRegistration usa allowlist/SSRF y no reenvía credenciales a destino no autorizado;
- IDs legacy se preservan mediante binding;
- approvals exact_action/scoped siguen siendo distintos;
- negocio + idempotency record son atómicos en Core cuando comparten DB;
- contexto histórico debe ser reproducible;
- Task dependencies bloqueantes forman DAG;
- Artifact separa authority, producer y custodian;
- PlanningService pertenece al Core y Core no crea Jobs directamente;
- authorization → certification → admission → autonomy ceiling;
- blocked != A0.

No reintroducir como contratos activos: `HumanInterval`, `HumanIntervalRequirement`, `ComparabilityResult`, `ApprovalGrant`, `AIReservation`, `ExecutionAdmission`.

No afirmar que algo está verificado si la prueba real no se ejecutó. Mantener compatibilidad standalone cuando la Spec lo permite. No acceder a SQLite privado de otra app. Toda acción irreversible/sensible requiere la confirmación correspondiente.
