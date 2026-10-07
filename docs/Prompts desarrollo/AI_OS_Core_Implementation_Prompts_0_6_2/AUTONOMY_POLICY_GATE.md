# Gate previo a P15 — AutonomyPolicyDefinition

P15 no puede inventar la semántica operativa de autonomía.

Antes de ejecutarlo debe existir una policy/configuración versionada y aceptada que defina:
- significado de A0–A5;
- acciones permitidas/prohibidas;
- approvals por nivel;
- autoridad para cambiar nivel;
- promoción, degradación y revocación;
- métricas, ventanas y umbrales;
- clases siempre humanas;
- límites A5 de repair: intentos, coste, duración, acciones, stop conditions y escalado;
- comportamiento ante Policy/Certification/Admission blocked/unknown;
- revisión e `invalidates_if_changed`.

P15 sólo puede comenzar con AcceptanceRecord vigente de esa definición.
