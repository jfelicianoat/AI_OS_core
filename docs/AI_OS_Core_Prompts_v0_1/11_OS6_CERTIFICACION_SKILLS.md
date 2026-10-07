# Fase 11 — Certificación automática de skills ante cambios de modelo/runtime

## OBJETIVO REAL

Evitar que una actualización de modelo local, runtime, quantization, chat template, skill o toolset se considere compatible por herencia.

## FLUJO

`model.changed / skill.updated / runtime.changed`
→ AI OS Core identifica fingerprints afectados
→ crea `CertificationRequest`
→ Model Drift ejecuta suite
→ emite resultado
→ AI OS actualiza disponibilidad efectiva
→ Broker/Agora filtran ejecución cuando corresponda.

## FINGERPRINT BLOQUEANTE

- model family/version
- artifact hash si existe
- quantization
- runtime/version
- chat template hash
- skill/version/instructions hash
- toolset schema hashes
- policy version

## REGLAS

Nueva combinación => UNKNOWN.

Estados:
- UNKNOWN
- TESTING
- CERTIFIED
- DEGRADED
- FAILED
- REVOKED

## SUITES

Cada skill crítica debe tener:
- casos normales;
- límites;
- negativos;
- forbidden actions;
- tool failures;
- schema adherence;
- trajectory checks;
- fuentes/citas si aplican.

## OVERRIDE

Sólo manual, con:
- aprobación;
- motivo;
- expiración;
- audit event.

## VERIFICACIÓN

- actualizar Qwen sin cambiar API invalida aplicabilidad anterior;
- cambio sólo de skill también;
- DEGRADED sigue policy;
- FAILED bloquea;
- override expira;
- evaluación no contamina aprendizaje de routing del Broker.
