# Mapa lógico de repositorios/procesos

| Nombre lógico | Nombre/ruta observada | Proceso/rol | Ubicación inicial | Estado |
|---|---|---|---|---|
| AI OS Core | `AI_OS_core` | control plane | PC principal | nuevo |
| Agora | `Agora` | Board/API | PC principal | existente |
| Agora Runner | mismo proyecto Agora | runner de Jobs | PC IA | existente |
| Gestión Tareas IA | `Gestion Tareas IA` | Tasks/calendario | PC principal | existente |
| Athena | `Athena` | Agent Runtime | junto al workspace | existente |
| Model Drift | `Model_Drift` | evaluación/certificación | por confirmar despliegue | existente |
| Knowledge Orchestrator | `Knowledge_Orchestrator` | knowledge | PC principal | existente |
| Local AI Lab | `Local AI Lab` | laboratorio | según experimento | opcional |
| YT Capture | `YT_Capture_Plugin` | captura | navegador | existente |
| ChatyGPT | `ChatyGPT` | UI | PC principal | existente |
| AI Broker | localizar repositorio servidor real | inference/routing | PC IA | **pendiente de identificar** |

Regla: ningún prompt puede crear un repositorio alternativo por una diferencia de nombre. Antes de modificar, registrar repo/ref/commit realmente inspeccionado.
