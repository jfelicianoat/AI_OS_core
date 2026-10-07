# Guía de verificación de la Spec 0.4

Ejecutar:

```bash
python verify_spec.py
```

## Resultados

### FAIL
Existe una incoherencia estructural. No se deben derivar prompts.

### CONSISTENT_DRAFT
La estructura es coherente, pero hay decisiones normativas todavía pendientes de aprobación humana. Éste es el resultado esperado de esta entrega.

### APPROVED_FOR_PROMPT_DERIVATION
Sólo debe aparecer después de:
- marcar las decisiones obligatorias como `approved`;
- actualizar Acceptance Registry;
- ejecutar de nuevo el verificador sin errores.

## Qué comprueba el verificador

- fuente normativa única;
- contratos canónicos no duplicados;
- requisitos con owner, fase, contratos y tests;
- todos los contratos usados están registrados;
- milestones cubiertos;
- dependencias de fases sin ciclos;
- casos de aceptación conocidos;
- puerta documental pre-P01 completa.

## Qué NO comprueba

No valida:
- APIs reales;
- código existente;
- seguridad en ejecución;
- rendimiento;
- comportamiento de SQLite ante hardware real;
- capacidad del Broker;
- integración efectiva entre apps.

Eso corresponde a fases posteriores y pruebas reales.
