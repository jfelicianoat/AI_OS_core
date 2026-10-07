# Fase 06 — Gestión-tareas-IA: planificación humana + IA

## OBJETIVO REAL

Conservar el calendario humano actual y añadir tareas IA paralelas, híbridas y dependencias entre ambas sin solapamientos falsos.

## PRINCIPIO

El calendario humano y la capacidad IA son recursos distintos.

Una tarea IA de 3 horas NO bloquea 3 horas humanas si sólo necesita 5 minutos de intervención.

## CAMBIOS DE DOMINIO

### actor
- human
- ai
- hybrid
- system

### duration
- wall_clock_estimate
- human_active_estimate
- ai_compute_estimate
- confidence
- source: manual/historical/statistical/heuristic

### dependencias
- finish_to_start
- start_to_start
- finish_to_finish
- human_approval
- artifact_required
- resource_required

Soportar:
- H→H
- H→AI
- AI→H
- AI→AI

### AI resource requirements
- cpu
- gpu
- npu
- ram
- model/capability
- exclusive resource.

## CALENDARIO

Mantener Google Calendar como fuente externa de solo lectura.

No permitir al AI OS Core modificar Google Calendar directamente.

Bloqueo humano basado principalmente en `human_active_estimate`.

## AI CAPACITY

Consumir snapshots/estimaciones de AI Broker.

Usar inicialmente P80 para planificación normal y P95 para deadlines críticos.

## TASK ↔ JOB

Una Task puede tener 0..N Jobs en Agora.

Ruta:
`Task ready → create_job_request → Agora`

Agora devuelve Job ID y después publica estados.

## REPLANIFICACIÓN

Si la ETA de un Job cambia:
- sólo replanificar calendario humano si una dependencia AI→H queda afectada.

## UI

Añadir de forma comprensible:
- actor;
- dependencias;
- tiempo humano;
- tiempo IA;
- estado de Jobs;
- bloqueo por IA/recurso.

Evitar convertir la agenda en un dashboard técnico.

## VERIFICACIÓN

Casos obligatorios:
1. IA 2h + humano 0m no bloquea calendario humano.
2. IA termina tarde y retrasa una tarea humana dependiente.
3. dos Jobs compiten por misma GPU.
4. H→AI→AI→H.
5. Broker unavailable produce estado recuperable.
6. Google Calendar sigue read-only.
7. app funciona sin AI OS Core.
