# AI OS Core — Kit de prompts de implementación v0.1

Este paquete contiene los prompts por fases para implementar el **AI OS Core** y adaptar de forma mínima los proyectos existentes.

## Orden de ejecución recomendado

1. `00_OS0_CONTRATOS_Y_REGLAS.md`
2. `01_OS1_CORE_FUNDACION.md`
3. `02_OS1_REGISTRY_EVENTS_POLICIES.md`
4. `03_OS2_AI_BROKER_MODEL_DRIFT.md`
5. `04_OS2_ATHENA.md`
6. `05_OS2_AGORA.md`
7. `06_OS4_GESTION_TAREAS_IA.md`
8. `07_OS2_KNOWLEDGE_ORCHESTRATOR.md`
9. `08_OS3_CHATYGPT_UI.md`
10. `09_OS2_LOCAL_AI_LAB_Y_YT_CAPTURE.md`
11. `10_OS5_INTEGRACION_END_TO_END.md`
12. `11_OS6_CERTIFICACION_SKILLS.md`
13. `12_OS7_CONTEXT_ENGINE.md`
14. `13_OS8_POLICY_ENGINE_Y_AUTONOMIA.md`

## Principio operativo

No implementar fases posteriores antes de que la anterior cumpla sus puertas de aceptación.

Cada prompt:
- es autosuficiente;
- separa responsabilidades por repositorio;
- exige pruebas;
- prohíbe inventar capacidades o estados;
- mantiene compatibilidad standalone de cada aplicación;
- evita acciones irreversibles sin confirmación humana.

## Repositorios implicados

- `AI_OS_Core` — nuevo
- `AI_Broker`
- `Model_Drift`
- `Athena`
- `Agora_AGR`
- `Gestion-tareas-IA`
- `Knowledge_Orchestrator`
- `ChatyGPT`
- `Local-AI-Lab`
- `YT_Capture_Plugin`

## Arquitectura de referencia

```text
AI OS Core            → ¿QUÉ queremos conseguir?
Context Engine         → ¿QUÉ necesitamos saber?
Capability Registry    → ¿QUÉ sabemos hacer?
Policy Engine          → ¿QUÉ podemos permitir?
Gestión de Tareas      → ¿CUÁNDO debe hacerse?
Agora / Athena         → ¿CÓMO lo hacemos?
AI Broker              → ¿CON QUÉ inteligencia?
Model Drift            → ¿Sigue funcionando bien después del cambio?
Knowledge Orchestrator → ¿QUÉ sabemos y qué evidencia lo respalda?
```
