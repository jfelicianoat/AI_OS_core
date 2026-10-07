# Prompt 11 — OS-6: automatización de certificación

## DIFERENCIA CON PROMPT 03
Prompt 03 añade contratos y certificación **manual**.
Este prompt añade reacción automatizada a cambios.

## PARTICIPAN
- AI OS Core
- AI Broker
- Model Drift
- Athena/Agora como consumidores del gate

## TRIGGERS
- model identity evidence changed;
- skill.updated;
- runtime.changed;
- toolset.changed;
- policy revision changed.

No todo cambio de hash = cambio real.
Primero ejecutar `ComparabilityAssessment`.

## FLUJO
1. Core recibe evidencia nueva.
2. Determina si cambia comparabilidad/aplicabilidad.
3. Si corresponde, crea CertificationRequest durable.
4. Model Drift ejecuta.
5. Devuelve resultado histórico.
6. Core calcula Applicability actual.
7. CapabilityAvailability se actualiza.
8. Ningún veredicto histórico se reescribe.

## ROUTING GATE
Para requirement obligatorio:
- definir candidate set certificado;
- pasar restricción al punto que sirve inferencia;
- comprobar effective model;
- fallback fuera de set => failure, no warning.

## CACHE/OUTAGE
- certification cache incluye revision/freshness;
- mandatory + indeterminate/stale beyond policy => block;
- advisory => policy explícita.

## PRUEBAS
- new evidence but same model not falsely marked regression;
- changed quantization invalidates applicability;
- effective fallback captured;
- Model Drift offline;
- duplicate CertificationRequest idempotent.
