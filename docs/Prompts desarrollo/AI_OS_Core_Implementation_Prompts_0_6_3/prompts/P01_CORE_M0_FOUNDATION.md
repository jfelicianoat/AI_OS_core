# P01 — AI OS Core M0: fundación determinista

## ROL
Backend architect/developer senior del control plane.

## OBJETIVO REAL
Construir el Core aislado que satisface los requisitos M0 asignados a P01.

## BASELINE NORMATIVA OBLIGATORIA

Trabaja contra **AI OS Core Normative Specification 0.6.1**, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`. Lee `NORMATIVE_SPEC_0_6_1.md` y `GLOBAL_RULES.md` antes de programar. Si el repo real contradice la Spec, devuelve `SPEC_GAP_REPORT` y no cambies silenciosamente ownership, contratos o invariantes.

Antes de cerrar esta fase, aplica `PHASE_ACCEPTANCE_PROTOCOL.md`; un resultado técnico no equivale a aceptación formal.

## REPOSITORIOS AFECTADOS
AI_OS_Core.

## PRERREQUISITOS
El paquete normativo canónico devuelve SpecApproved=YES y PreP01Ready=YES. Referenciar salida del verificador y AcceptanceRecords; `P00 PASS` textual no basta.

## ENTRADAS
Artefactos P00, Spec y repo actual.

## TAREA Y CAMBIOS EXACTOS
Implementar FastAPI/Pydantic v2 + SQLite única WAL/synchronous=FULL + migrations forward-only. Entregar Service/Capability Registry, Goals/Objectives, Resource Graph+IdentityBinding, idempotencia atómica, Audit/DecisionTrace, Event inbox/store/ReplayCursor/full_state projection/quarantine/REPLAY_GAP, restore con OperationStatusQuery/OperationExecutionStatus/OperationReceipt contra receptor simulado, ServiceRegistration allowlist/SSRF/no credential forwarding, resource/adapter revisions, health y paginación estable. Sólo full_state modifica la proyección canónica M0–M2.

## NO HACER
No approvals, budget, Policy completo, Planner, Tasks/Jobs ni integración real externa.

## VERIFICACIÓN CON FIXTURES / PRUEBAS AISLADAS
C01,C02,C03,C05,C15,M0-REG y pruebas explícitas de `M0-GOALS`, `M0-RESOURCE-GRAPH`, `M0-AUDIT`, `C23` y `C24`; incluir concurrencia y restart.

## PRUEBAS REALES
No requiere servicios reales; red sólo contra fakes controlados.

## EVIDENCIAS A ENTREGAR
OpenAPI snapshot, migrations, tests, ejemplos de replay/quarantine/restore.

## CRITERIOS DE ACEPTACIÓN
Core arranca con cero dependencias; requisitos P01 verdes; no acceso a DB privada externa.

## FORMATO DE SALIDA DEL AGENTE
Findings, cambios por archivo, tests, evidencia, riesgos,; TECHNICAL_RESULT; ACCEPTANCE_CANDIDATE si aplica; GATE_STATUS.
