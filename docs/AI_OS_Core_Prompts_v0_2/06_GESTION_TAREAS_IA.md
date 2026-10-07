# Prompt 06 — Gestión de Tareas IA: tiempo humano, IA y reservas

## FASE ARQUITECTÓNICA
OS-4 planning.

## OBJETIVO
Planificar humano+IA sin equiparar wall-clock con agenda humana.

## TASK ACTOR
- human
- ai
- hybrid
- system

## TIEMPO HUMANO
No basta `human_active_estimate` total.
Añadir `HumanIntervalRequirement`:
- relative position: start/end/after artifact/etc.;
- duration;
- earliest/latest;
- required presence;
- interruptible;
- resource/user.

Ejemplo híbrido:
- 5 min inicio;
- 2h IA;
- 15 min revisión final.

## IA
Separar:
- queue wait;
- service/compute;
- wall clock.
P80/P95 son estimadores, no SLA.
No sumar percentiles como si produjeran automáticamente percentil end-to-end.

Si `sample_count` insuficiente:
- usar heuristic con `confidence=low`;
- margen configurable;
- mostrar incertidumbre.

## ADMISSION/RESERVATION
Capacity snapshot sólo observa.
Definir quién reserva/admite:
- Broker/Runner/Resource Manager real.
Gestión Tareas solicita `AIReservation` o recibe `AdmissionResult`.
Sin reserva, marcar scheduling como provisional.

## RECURSOS
- GPU/VRAM/RAM/CPU;
- exclusive/shared;
- lease start/end;
- release on cancel/failure.

## DEPENDENCIAS
Incluir intervalos humanos de tareas híbridas en replanificación.
Rechazar ciclos.

## GOOGLE CALENDAR
Sigue read-only.

## PRUEBAS
- intervención inicio+fin;
- dos Jobs GPU exclusiva;
- ETA cambia y desplaza revisión humana;
- DST/timezone;
- no historial;
- Task multi-job con policy all_required y partial failure.
