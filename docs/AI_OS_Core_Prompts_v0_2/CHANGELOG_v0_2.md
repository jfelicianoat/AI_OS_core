# Changelog v0.2

## Correcciones principales

- Se elimina la afirmación de que OS-0 está cerrado.
- Se pasa de contratos `1.0` a `0.2` pre-1.0.
- Se separa número de prompt de fase arquitectónica.
- Se añade inventario único de contratos, tipos anidados y contratos reservados.
- Se define semántica de Policy con UNKNOWN, combinación de restricciones y obligaciones.
- Se endurece Approval con `action_digest`, versiones de recursos, principal autorizado, consumo y expiración.
- Se separan:
  - identidad/fingerprint observado;
  - comparabilidad;
  - veredicto de certificación;
  - aplicabilidad actual.
- Se añade gate de modelo efectivo servido, incluidos fallbacks.
- Context Package pasa a exigir evidencia reproducible del contenido efectivamente consumido.
- Se define frontera transaccional para eventos, idempotencia e internal outbox.
- Se añade replay/delivery durable desde productores y `resource_revision`/`source_sequence`.
- Se revisa durabilidad SQLite: `NORMAL` no se presenta como garantía frente a power loss.
- Se añade adaptación entre IDs globales y IDs nativos, sin renombrar objetos existentes.
- Se añaden máquinas de estados y reglas de agregación Task/Job/Goal.
- Planificación híbrida usa intervalos humanos, no sólo un total.
- Se distingue capacidad observada de reserva/admisión real.
- Se añade autorización por principal y protección SSRF/service endpoint allowlist.
- Se sincroniza roadmap: OS-8 Policy, OS-9 Planner, OS-10 Autonomía.
- Se corrigen catálogos/eventos, health vocabularies, Artifact ownership y nombres de repositorios.
- Se reduce el MVP del Core a tres recorridos prioritarios antes de ampliar superficie.
