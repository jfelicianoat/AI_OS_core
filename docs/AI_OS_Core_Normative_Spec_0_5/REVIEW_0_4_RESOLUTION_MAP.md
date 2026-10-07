# Mapa de resolución de la revisión 0.4

| Hallazgo | Resolución en 0.5 |
|---|---|
| N01 verificador aprobaba sin evidencia | tres gates; lee registry, acceptance, tests y manifest; exige decisiones obligatorias y AcceptanceRecord válidos |
| N02 registry no fiel | M0 y M2 se enumeran exhaustivamente; provider_phases y verifier_phases separados; M2-minimal/contextual |
| N03 tests nominales sin cobertura real | `test_catalog.json` declara `covers` y resultado esperado; verifier cruza ambos sentidos |
| N04 restore confundía receipt de evento y ejecución | nuevos OperationStatusQuery/OperationExecutionStatus/OperationReceipt |
| N05 bordes Policy | unconditional vacío, constraints incompatibles y Approval+security UNKNOWN definidos |
| N06 autonomía incompleta | authorization→certification→admission→ceiling; blocked != A0 |

## Ajustes complementarios
- `ExecutionAdmission` se divide en WorkerAdmission e InferenceAdmission.
- P02 entrega BudgetReservation y CertificationApplicability projection.
- P10 sólo verifica.
- deltas siguen fuera de proyección canónica M0–M2.
