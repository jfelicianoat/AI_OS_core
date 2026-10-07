# Prompt 00A — Normalización documental e inventario normativo

## FASE ARQUITECTÓNICA
OS-0 — preparación documental.

## OBJETIVO REAL
Convertir OS-0/OS-1 y el kit en fuentes legibles y no ambiguas antes de definir contratos ejecutables.

## PRERREQUISITOS
Ninguno. No modificar código de producto.

## TAREA
1. Normalizar Markdown:
   - eliminar escapes editoriales espurios (`&#x20;`, encabezados escapados, guiones bajos escapados);
   - conservar literalmente el significado original;
   - no “arreglar” semántica durante esta limpieza.
2. Separar en cada bloque:
   - **normativo**;
   - **ejemplo**;
   - **pseudocódigo**;
   - **decisión futura**.
3. Crear `CONTRACT_INVENTORY.md` con todas las piezas usadas en la arquitectura:
   - entidades top-level;
   - tipos anidados;
   - mensajes/comandos;
   - proyecciones;
   - contratos reservados.
4. Como mínimo inventariar:
   ResourceReference, Goal, Objective, CapabilityManifest, SkillManifest,
   ExecutionFingerprint, ModelIdentityEvidence, ComparabilityResult,
   Certification, CertificationApplicability, CertificationRequest, Event,
   Policy, PolicyDecision, PolicyObligation, ConstraintSet, ContextRequest,
   ContextPackage, Decision, Task, TaskDependency, HumanInterval,
   AICapacitySnapshot, AIReservation/AdmissionResult, AIDurationEstimate,
   Job, JobDispatch, CreateJobRequest/Response, AgentRun, Artifact,
   VerificationResult, Failure, ApprovalRequest, ApprovalDecision,
   ApprovalGrant, CommandEnvelope, ServiceRegistration, ServiceHealth,
   DecisionTrace.
5. Para cada contrato indicar:
   - propietario;
   - fase que lo introduce;
   - `schema_version` pre-1.0 (`0.2`);
   - top-level vs anidado;
   - persistido vs proyección vs efímero;
   - productor;
   - consumidores;
   - estado: `draft`, `approved_for_fixture`, `reserved`.

## CRITERIOS DE ACEPTACIÓN
- Markdown renderiza correctamente.
- Todos los bloques marcados como YAML son YAML real o están renombrados como pseudocódigo.
- No hay dos inventarios contradictorios.
- Ningún contrato usado por fases posteriores queda “implícito”.
- No se declara `1.0` ni “congelado”.
