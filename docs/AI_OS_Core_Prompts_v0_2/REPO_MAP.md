# Mapa lógico de repositorios y procesos

Este archivo evita crear repositorios duplicados por diferencias de nombre.

| Nombre lógico | Ruta/nombre observado en revisión | Rol | Máquina inicial | Autoridad |
|---|---|---|---|---|
| AI OS Core | `AI_OS_core` / nuevo servicio | control plane | PC principal | Goals, Objectives, relaciones, policies globales |
| Agora | `Agora` (no asumir `Agora_AGR`) | Board/API + Runner | Board/API PC principal; Runner PC IA | Jobs integrados |
| Gestión de Tareas IA | `Gestion Tareas IA` | calendario/Tasks | PC principal | Tasks y scheduling |
| Athena | `Athena` | runtime de agente | donde esté el workspace | Agent Runs |
| Model Drift | `Model_Drift` | evaluación/certificación | PC principal o laboratorio | resultados de evaluación |
| Knowledge Orchestrator | `Knowledge_Orchestrator` | conocimiento | PC principal | documentos/claims |
| Local AI Lab | `Local AI Lab` | laboratorio | según experimento | experimentos propios |
| YT Capture Plugin | `YT_Capture_Plugin` | captura | navegador | capturas |
| AI Broker | **resolver contra repositorio servidor real antes de modificar** | inferencia/routing | PC IA | modelos/inferencias |
| ChatyGPT | `ChatyGPT` | UI | PC principal | estado local de chat/UI |

## Regla

Antes de aplicar cualquier prompt que modifique un repositorio:
1. localizar el repositorio real;
2. leer `CURRENT_STATE.md`/README/contrato público vigente;
3. registrar commit/ref analizado;
4. no crear un repo nuevo si ya existe uno con nombre diferente;
5. si AI Broker no se identifica con certeza, detener sólo ese bloque y documentar la evidencia faltante.
