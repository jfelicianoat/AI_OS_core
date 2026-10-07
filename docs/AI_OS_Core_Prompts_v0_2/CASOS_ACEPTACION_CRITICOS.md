# Casos de aceptación críticos

Estos casos deben resolverse en documentación antes de automatizarse y luego convertirse en pruebas.

1. Dos comandos idénticos llegan simultáneamente; tras reinicio llega de nuevo.
2. `job.completed` llega antes que un `job.started` retrasado.
3. Core permanece apagado mientras Agora/Broker producen eventos.
4. Approval vence después de mostrarse en UI pero antes de ejecutar.
5. Payload/destino cambia después de aprobación.
6. Broker intenta fallback a modelo no certificado.
7. Identidad del modelo obtiene un nuevo dato antes desconocido sin evidencia de cambio real.
8. KO modifica/expira una fuente tras un Run histórico.
9. Task `all_required` tiene 3 Jobs: 2 success, 1 failed.
10. Task híbrida: humano inicio + IA larga + humano revisión.
11. Dos Jobs requieren GPU exclusiva simultáneamente.
12. Servicio registra `base_url` fuera de allowlist.
13. Principal intenta consultar recurso de otro scope.
14. Evento legítimo tiene payload incompatible con misma `resource_revision`.
15. Restore de DB y replay de outboxes sin duplicar efectos.
