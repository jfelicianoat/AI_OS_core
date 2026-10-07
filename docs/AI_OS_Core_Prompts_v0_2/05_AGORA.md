# Prompt 05 — Agora: adaptación de identidad y Jobs integrados

## FASE ARQUITECTÓNICA
OS-2.

## OBJETIVO
Adaptar Agora sin sustituir su identidad nativa ni su Board.

## IDENTIDAD
No convertir filename Card ID en ULID.
Añadir binding/adaptador:
- global Job ID;
- board/instance;
- native filename/card identity;
- native revision si existe.

No asumir `external_reference` única.

## COMPATIBILIDAD
Los contratos actuales con `extra=forbid` requieren:
- endpoint/version nuevo, o
- wrapper/adaptador,
no añadir campos desconocidos silenciosamente.

## JOB EVENTS
Unificar catálogo:
- job.created
- job.claimed
- job.started
- job.blocked
- job.completed
- job.failed
- job.cancelled
- artifact.created
- worker.available/unavailable

Con source sequence/resource revision.

## CERTIFICATION GATE
Antes de claim/dispatch:
- validar requirement;
- pero revalidar también en punto de inferencia (no confiar sólo en pre-check).

Si Core/Model Drift están inaccesibles:
- requirement `mandatory` => bloquear;
- requirement `advisory` => seguir policy explícita;
- nunca usar cache stale como permiso sin regla.

## EXCLUSIVIDAD
Documentar: Agora es autoridad de Jobs del flujo AI OS integrado, no de toda operación durable del ecosistema.

## PRUEBAS
- binding persiste tras rename/import según reglas acordadas;
- retry no crea otra Card;
- blocked event soportado;
- job completed tardío no es revertido por started atrasado;
- standalone sigue operativo.
