# Nombres canónicos de contratos v0.3

| Concepto | Nombre canónico | Owner |
|---|---|---|
| referencia federada | ResourceReference | contrato común |
| binding global/nativo | IdentityBinding | AI OS Core |
| objetivo | Goal | AI OS Core |
| objetivo intermedio | Objective | AI OS Core |
| capacidad | CapabilityManifest | proveedor/Core projection |
| skill | SkillManifest | runtime |
| identidad de modelo | ModelIdentityEvidence | AI Broker |
| huella de ejecución | ExecutionFingerprint | runtime |
| comparabilidad | ComparabilityAssessment | Model Drift |
| veredicto evaluación | EvaluationVerdict | Model Drift |
| certificación histórica | Certification | Model Drift |
| aplicabilidad | CertificationApplicability | AI OS Core |
| solicitud certificación | CertificationRequest | Core→Model Drift |
| evento | EventEnvelope | productor |
| comando | CommandEnvelope | solicitante |
| policy | Policy | AI OS Core |
| decisión policy | PolicyDecision | AI OS Core |
| obligación | PolicyObligation | AI OS Core |
| restricciones | ConstraintSet | AI OS Core |
| solicitud aprobación | ApprovalRequest | AI OS Core |
| autorización aprobada | ApprovalAuthorization | AI OS Core |
| uso aprobación | ApprovalUse | AI OS Core |
| revocación | ApprovalRevocation | AI OS Core |
| estado efectivo approval | ApprovalEffectiveState | AI OS Core |
| Task | Task | Gestión Tareas |
| tramo humano | HumanWorkSegment | Gestión Tareas |
| dependencia | TaskDependency | Gestión Tareas |
| forecast IA | AICapacityForecast | Broker/Agora adapter |
| admisión ejecución | ExecutionAdmission | Agora/Broker |
| Job | Job | Agora |
| dispatch Job | JobDispatchRequest | Task Manager→Agora |
| Run | AgentRun | Athena |
| artifact | Artifact | owner/custodian declarado |
| verification | VerificationResult | verifier |
| contexto | ContextPackage | AI OS Core |
| propuesta Planner | TypedPlanProposal | AI OS Core |
| trace | DecisionTrace | AI OS Core |

Nombres retirados:
- HumanInterval / HumanIntervalRequirement → HumanWorkSegment
- ComparabilityResult → ComparabilityAssessment
- AIReservation queda fuera del MVP
- ApprovalGrant → ApprovalAuthorization + ApprovalUse + ApprovalRevocation
