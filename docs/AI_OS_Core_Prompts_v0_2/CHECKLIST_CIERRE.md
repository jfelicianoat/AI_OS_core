# Checklist de cierre revisado

## Documental
- [ ] No quedan escapes/editorial corruption.
- [ ] Contratos top-level/anidados/reservados inventariados.
- [ ] Ningún contrato se denomina 1.0 antes de aprobación.
- [ ] Campos tienen obligatoriedad/null/formato/unidad.
- [ ] R0–R4 definidos.
- [ ] Nombres lógicos y repos reales mapeados.

## Policies / Approvals
- [ ] UNKNOWN definido.
- [ ] Constraints se acumulan.
- [ ] Approval ligado a action digest y resource revisions.
- [ ] Principal autorizado y consumo definidos.
- [ ] Athena conserva autoridad local de permisos.

## Certification
- [ ] Identity evidence conserva status/provenance.
- [ ] Certification histórica ≠ Applicability actual.
- [ ] Effective model se registra.
- [ ] Fallback fuera de set certificado se bloquea cuando mandatory.

## Context
- [ ] Contenido consumido es recuperable o materializado.
- [ ] Hash no se confunde con retención.
- [ ] Expiración de uso y evidencia histórica separadas.

## Events
- [ ] Producer outbox/replay.
- [ ] ACK tras persistencia.
- [ ] source_sequence/resource_revision.
- [ ] late event no revierte.
- [ ] poison event y replay manual.
- [ ] idempotency concurrente probada.

## Durabilidad
- [ ] Garantía NORMAL/FULL documentada.
- [ ] RPO/RTO declarados como target.
- [ ] restore test plan.

## Identity/State
- [ ] legacy IDs no migrados por fuerza.
- [ ] IdentityBinding.
- [ ] state transitions.
- [ ] Task multi-job aggregation.
- [ ] cycle detection.
- [ ] optimistic concurrency.

## Scheduling
- [ ] human intervals.
- [ ] queue vs compute.
- [ ] capacity observation vs reservation.
- [ ] timezone/DST.
- [ ] insufficient-history fallback.

## Security
- [ ] principal authorization matrix.
- [ ] endpoint allowlist/SSRF controls.
- [ ] exclusion privacy.
- [ ] secrets absent logs/events.

## MVP
- [ ] tres recorridos de valor demostrables.
- [ ] optional integrations do not block.
- [ ] standalone behavior preserved.
