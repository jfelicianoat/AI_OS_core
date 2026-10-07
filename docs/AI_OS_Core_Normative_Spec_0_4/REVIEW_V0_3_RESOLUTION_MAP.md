# Mapeo de la revisión v0.3 → Specification 0.4

| Observación | Resolución normativa 0.4 |
|---|---|
| V01 precedencia dual | Una sola precedencia en `NORMATIVE_SPEC_0_4.md`; README futuros deben remitir, no duplicar |
| V02 outputs P00 incompletos | Puerta pre-P01 incluye inventario, diccionario, state tables, auth matrix, event authority, persistence map, schemas, fixtures y Acceptance Registry |
| V03 dependencias E2E | M2 coverage asigna owner, contrato, fase y test; P02 entrega BudgetReservation y CertificationApplicability projection |
| V04 outbox “cuando sea posible” | Dos guarantee profiles: transactional outbox o `reconciliable_state_only`, con límites explícitos |
| V05 deltas | M0–M2 sólo `full_state` cambia proyección; delta application diferida |
| V06 approval→execution | ApprovalUse + Command/outbox se comprometen en la misma transacción; max_uses/digest/revocation validados antes |
| V07 C15 sin fase | M0 prueba restore con receptor simulado; M2 con receptores reales que soporten receipt/status |
| V08 version/impact | `AcceptanceRecord` modela revisión, evidencias, dependencias e invalidación por cambios incompatibles |

## Decisiones adicionales

- `ExecutionAdmission` se divide en `WorkerAdmission` (Agora) e `InferenceAdmission` (Broker).
- `confirmed` en scheduling significa admisión al inicio, no reserva futura de GPU.
- una Policy con `conditions=[]` sólo es válida con `unconditional=true`.
- presupuesto mínimo ya existe en P02, no se difiere a P13.
