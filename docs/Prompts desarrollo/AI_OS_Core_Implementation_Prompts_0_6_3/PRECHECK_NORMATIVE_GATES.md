# Precheck normativo obligatorio

Baseline: Spec 0.6.1, SHA-256 `d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`.

Define `NORMATIVE_PACKAGE_PATH` apuntando al paquete normativo canónico vigente. Debe contener `NORMATIVE_SPEC_0_6_1.md`, `spec_registry.json`, `test_catalog.json`, `acceptance_registry.json`, `manifest.json` y `verify_spec.py`.

El snapshot completo usado para derivar este kit está en `reference/normative_package_0_6_1/`, pero no sustituye al registro canónico si sus AcceptanceRecords han cambiado.

## PRECHECK-SPEC
1. verificar el hash de la Spec;
2. ejecutar `python -S verify_spec.py` dentro de `NORMATIVE_PACKAGE_PATH`;
3. exigir `CandidateConsistency: PASS` y `SpecApproved: YES` antes de habilitar ejecución;
4. conservar ruta/URI, salida del verificador y refs de AcceptanceRecords.

`CONSISTENT_DRAFT` no equivale a aprobación formal.

## PRECHECK-P01
P01 sólo puede comenzar cuando el paquete canónico devuelve `PreP01Ready: YES`. La mera existencia de los nueve documentos no basta.

## PRECHECK-P03
Antes de P03 debe existir un inventario aceptado del servidor Broker real con repo/ruta, commit/ref, entrypoint/proceso, APIs observadas y fecha. Debe tener AcceptanceRecord vigente.

Los agentes preparan evidencia/candidatos de aceptación, pero no fabrican aprobación humana.
