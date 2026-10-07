# Verification Guide — Spec 0.6.1

Ejecutar:

```bash
python -S verify_spec.py
```

## Gates

### CandidateConsistency
Verifica estructura y trazabilidad documental:
- fuente normativa/hash/predecencia exactos;
- catálogo contractual exacto;
- decisiones e invariantes obligatorios;
- anchors `INV-*` presentes en la fuente;
- M0/M2 exactos;
- owners/providers/verifiers;
- proveedor no puede ser una fase P10 de verificación;
- cada provider precede o coincide con su verifier;
- cobertura Requirement→Test y Test→Requirement;
- pre-P01 por identidad exacta;
- AcceptanceRecords y dependencias transitivas;
- concordancia ID/revisión/hash de decisión y aceptación.

### SpecApproved
Además:
- todas las decisiones obligatorias `approved`;
- AcceptanceRecord `accepted` vigente para la revisión/hash exactos;
- accepted_by, accepted_at y evidence_refs;
- todas sus dependencias transitivas vigentes.

### PreP01Ready
Además:
- los nueve artefactos pre-P01 existen;
- cada uno tiene revisión/hash propios;
- declara compatibilidad con la Spec 0.6.1;
- AcceptanceRecord vigente y dependencias vigentes.

## Alcance limitado

El verificador comprueba **coherencia y trazabilidad declarada**.

No demuestra automáticamente que:
- la semántica de un caso de prueba sea suficiente;
- el código real implemente la Spec;
- una integración funcione;
- una Policy sea segura en todo escenario.

La cobertura semántica de los tests se revisa humanamente y, más adelante, mediante pruebas implementadas.


## Sincronización Markdown ↔ registro

El verificador 0.6.1 compara de forma explícita:
- la lista de precedencia escrita en `NORMATIVE_SPEC_0_6_1.md`;
- la lista M0 del apartado 14.1;
- la lista M2-minimal del apartado 14.2;
- la ampliación M2-contextual del apartado 14.3;
- el nombre exacto del artefacto `DOC-CONTRACT-SCHEMAS`.

Estas comprobaciones son acotadas. El verificador no intenta interpretar automáticamente toda la prosa normativa.
