# AI OS Core — Kit de prompts de implementación v0.2 (revisado)

Estado: **borrador contractual revisable**.  
Esta versión sustituye al kit v0.1 y corrige los hallazgos de la revisión documental del 12/09/2026.

## Cambio de criterio

No se considera OS-0 “cerrado” ni se congela contrato `1.0` todavía.  
Los contratos se mantienen en **serie pre-1.0 (`0.2`)** hasta superar las puertas documentales y de integración definidas en este kit.

## Orden recomendado

### Bloque A — Cierre documental previo a código
1. `00A_NORMALIZACION_E_INVENTARIO.md`
2. `00B_CONTRATOS_MAESTROS.md`
3. `00C_POLICIES_APPROVALS_AUTH.md`
4. `00D_EVENTOS_IDEMPOTENCIA_DURABILIDAD.md`
5. `00E_IDENTIDADES_ESTADOS_Y_PERSISTENCIA.md`
6. `00F_PLAN_FISICO_REPOS_Y_MVP.md`

### Bloque B — AI OS Core MVP
7. `01_CORE_MVP_FUNDACION.md`
8. `02_CORE_REGISTRY_EVENTS_POLICIES.md`

### Bloque C — Adaptaciones por aplicación
9. `03_AI_BROKER_MODEL_DRIFT.md`
10. `04_ATHENA.md`
11. `05_AGORA.md`
12. `06_GESTION_TAREAS_IA.md`
13. `07_KNOWLEDGE_ORCHESTRATOR.md`
14. `08_CHATYGPT.md`
15. `09_LOCAL_AI_LAB_Y_YT_CAPTURE.md`

### Bloque D — Integración y evolución
16. `10_E2E_SIN_AUTONOMIA.md`
17. `11_CERTIFICACION_AUTOMATIZADA.md`
18. `12_CONTEXT_ENGINE.md`
19. `13_POLICY_ENGINE.md`
20. `14_PLANNER_TIPADO.md`
21. `15_AUTONOMIA_CONDICIONAL.md`

## Regla de ejecución

Cada prompt declara:
- prerrequisitos;
- repositorio(s) afectado(s);
- decisiones ya fijadas;
- decisiones prohibidas durante esa fase;
- entregables exclusivos;
- pruebas con fixtures;
- pruebas reales requeridas;
- evidencia de cierre.

No ejecutar una fase si sus prerrequisitos no están aprobados.

## Arquitectura de responsabilidades

```text
AI OS Core            → objetivos, estado federado, reglas, relaciones y trazabilidad
Gestión de Tareas     → calendario, Tasks y planificación humana/IA
Agora                 → Jobs del flujo integrado y ejecución durable de esos Jobs
Athena                → runtime de agente, permisos, verificación y repair
AI Broker              → modelos, routing e inferencia
Model Drift            → evaluación/certificación y comparabilidad
Knowledge Orchestrator → conocimiento y evidencia
ChatyGPT               → UI/cliente
Local AI Lab            → evidencia experimental opcional
YT Capture Plugin       → captura hacia KO
```

**Importante:** la exclusividad de Agora se limita a los **Jobs del flujo integrado**. No invalida la durabilidad propia de KO, Athena, Broker u otros subsistemas.
