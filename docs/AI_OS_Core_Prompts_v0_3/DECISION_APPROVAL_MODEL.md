# Decisión candidata — Approval model
Estado: proposed

## Entidades
ApprovalRequest: solicitud pendiente.

ApprovalAuthorization: términos inmutables aprobados:
- requester/approver principals
- scope_mode
- exact action digest o predicate scope
- resources + revisions
- capability/version
- policy revision
- expires_at
- max_uses
- risk ceiling

ApprovalUse: append-only:
- authorization_id
- operation_id
- concrete action digest
- effective resource revisions
- used_at
UNIQUE(authorization_id, operation_id)

ApprovalRevocation: append-only.

ApprovalEffectiveState: active/exhausted/expired/revoked/superseded.

## exact_action
Sólo digest exacto. Cambio de destino/payload/revision => no válido.

## scoped
La autorización define predicado/recursos/riesgo/expiry/max_uses.
Cada acción concreta produce un ApprovalUse con su digest.

## Retry
Retry de la misma operación conserva operation_id y no consume otro uso.

## Expiry/revocation
Se comprueban transaccionalmente antes de crear ApprovalUse.

## Athena
La autorización Core no eleva permisos. Athena valida trust + autorización y aplica su PermissionEngine.
