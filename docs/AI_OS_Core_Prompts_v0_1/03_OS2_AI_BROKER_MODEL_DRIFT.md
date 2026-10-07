# Fase 03 — Integración AI Broker + Model Drift

## OBJETIVO REAL

Conectar inteligencia, capacidad y certificación sin trasladar objetivos ni scheduling a estos proyectos.

# BLOQUE A — AI_Broker

## CAMBIOS MÍNIMOS

Añadir endpoints/adaptadores públicos para:

1. catálogo de modelos;
2. identidad/fingerprint observable;
3. capacidad actual;
4. estimaciones históricas;
5. lifecycle events.

### Fingerprint
Exponer cuando exista evidencia:
- provider;
- deployment;
- family;
- version;
- artifact hash;
- quantization;
- runtime/version;
- chat template hash;
- context configuration.

Lo no verificable = `null`.

### Capacity
Exponer:
- CPU/RAM/GPU;
- modelos unloaded/loading/ready/busy/unavailable;
- queue depth;
- estimated available time;
- confidence.

### Eventos
- `model.discovered`
- `model.changed`
- `model.removed`
- `model.capability_changed`
- `broker.capacity_changed`

### Estimación de duración
Exponer datos para calcular:
- P50;
- P80;
- P95;
- queue wait.

Basado en telemetría real, no en estimación del LLM.

## NO HACER
- no Goal Engine;
- no scheduler;
- no gestionar calendario;
- no certificar skills.

# BLOQUE B — Model_Drift

## CAMBIOS MÍNIMOS

Extender el producto para soportar:

- `CertificationRequest`;
- `Skill Certification Suite`;
- `Capability Regression Suite`;
- `ExecutionFingerprint`;
- `CertificationResult`.

Estados:
- unknown
- testing
- certified
- degraded
- failed
- revoked

La suite debe poder probar:
- tool calling;
- schema JSON;
- forbidden actions;
- adherencia a instrucciones;
- trayectoria agéntica;
- fuentes/citas;
- errores de herramientas;
- regresión de latencia/verbosidad cuando sea relevante.

## POLÍTICA

No usar score global para ocultar regresiones bloqueantes.
Mantener el enfoque actual de métricas con políticas de bloqueo.

## EVENTOS MODEL DRIFT
- `certification.started`
- `certification.completed`
- `certification.degraded`
- `certification.failed`
- `certification.revoked`

## INTEGRACIÓN CON CORE

AI OS Core:
- consume fingerprints/capacity de Broker;
- consume proyección de certificaciones;
- no ejecuta internamente las suites.

## VERIFICACIÓN

- cambio de modelo genera nuevo fingerprint;
- combinación nueva queda UNKNOWN;
- Model Drift puede producir CERTIFIED/DEGRADED/FAILED;
- Broker sigue funcionando si Core está apagado;
- Model Drift sigue funcionando standalone.
