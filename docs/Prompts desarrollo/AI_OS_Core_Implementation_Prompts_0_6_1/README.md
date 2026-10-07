# AI OS Core — Implementation Prompt Kit 0.6.1

Kit de implementación derivado de la Spec 0.6.1 ya definida. No rediseña arquitectura.

Orden recomendado:
1. P00 documentación pre-P01
2. P01 Core M0 foundation
3. P02 Policy/Approval/Security
4. P03 Broker + Model Drift
5. P04 Athena
6. P05 Agora
7. P06 Gestión Tareas IA
8. P07 Knowledge Orchestrator — sólo obligatorio para M2-contextual
9. P08 ChatyGPT
10. P09 opcionales — no bloquea M2
11. P10A M2-minimal E2E
12. P10B M2-contextual E2E
13. P11 auto-certification
14. P12 Context Engine
15. P13 Policy Engine completo
16. P14 Typed Planner
17. P15 Conditional Autonomy

P10 verifica; no crea funciones que debieron existir en P02–P08. P11 automatiza certification pero no crea por primera vez el model gate. P14 produce TypedPlanProposal y solicita Tasks a Gestión Tareas; no crea Jobs directamente.
