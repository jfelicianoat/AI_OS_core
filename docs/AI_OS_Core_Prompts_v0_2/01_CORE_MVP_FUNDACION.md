# Prompt 01 — Construir AI OS Core MVP

## FASE ARQUITECTÓNICA
OS-1.

## PRERREQUISITOS
00A–00F aprobados. Contratos `0.2` disponibles como fixtures.

## OBJETIVO
Implementar sólo el control plane necesario para los tres recorridos MVP.

## INCLUIR
- FastAPI + Pydantic v2.
- SQLite.
- migrations forward-only.
- Service Registry básico.
- Capability Registry básico.
- Goals/Objectives mínimos.
- Decisions.
- Resources/Relations.
- Event inbox/store + processing.
- Audit.
- Idempotency.
- AuthN/AuthZ mínima según matriz.
- Health propio.

## EXCLUIR EN ESTA FASE
- Planner;
- Context Engine federado;
- approvals complejas salvo almacenamiento mínimo si son prerequisito;
- automatic certification;
- Task scheduling;
- job dispatch;
- model routing.

## DURABILIDAD
Implementar perfiles acordados en 00D.
Tests deben diferenciar:
- process crash recovery;
- restart;
- no afirmar power-loss durability sin prueba/setting.

## EVENTOS
- persist + ACK;
- `(event_id, handler)` unique;
- resource revision ordering;
- delayed event no revierte projection.

## SEGURIDAD
- endpoint allowlist para service probes;
- principals y scopes;
- secrets fuera de DB/logs.

## ACEPTACIÓN
1. Core arranca con 0 dependencias.
2. Service/capability registration funciona.
3. Goal y Decision persistentes.
4. Resource graph trazable.
5. Duplicate request concurrente no duplica negocio.
6. Late event no revierte state.
7. Restart recupera processing.
8. Paginated list endpoints deterministas.
