# Decisión candidata — prerequisitos del E2E
Estado: proposed

| Requisito | Propietario | Prompt que lo entrega |
|---|---|---|
| approvals API/consume | AI OS Core | P02 |
| Task→Job idempotente | Gestión Tareas + Agora | P06 + P05 |
| agregación Job→Task | Gestión Tareas | P06 |
| forecast capacidad | Broker/Agora adapters | P03/P05 |
| admisión real | Agora + Broker | P05/P03 |
| candidate set permitido | AI Broker | P03 |
| effective model/fallback | Broker + Athena | P03/P04 |
| certification manual/query | Model Drift + Core | P03/P02 |
| context evidence | KO/Athena/Core | P07/P04 |
| UI trace | ChatyGPT | P08 |

MVP no promete hard reservation futura de GPU.
Task Manager usa forecast.
Admisión real sucede al ejecutar en Agora/Broker.
