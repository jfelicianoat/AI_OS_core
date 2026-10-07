# Protocolo común de cierre

Cada fase emite dos resultados diferentes.

## TECHNICAL_RESULT
- `PASS`: pruebas/entregables técnicos satisfechos.
- `FAIL`: incumplimiento demostrado.
- `BLOCKED`: falta prerrequisito, aceptación, entorno o prueba indispensable.

Diagnosticar correctamente un fallo de otra fase no convierte esta fase en PASS.

## GATE_STATUS
- `ACCEPTED`: existe AcceptanceRecord vigente que permite avanzar.
- `PENDING_ACCEPTANCE`: resultado técnico PASS, pendiente de aceptación formal.
- `BLOCKED`: no procede aceptar por fallos/prerrequisitos.

El agente puede producir `ACCEPTANCE_CANDIDATE` con artifact/hito, revisión/hash, evidence_refs, dependencias e `invalidates_if_changed`; no se autoaprueba.

Una fase posterior sólo hereda evidencia si AcceptanceRecord, contratos, builds y configuración siguen vigentes.
