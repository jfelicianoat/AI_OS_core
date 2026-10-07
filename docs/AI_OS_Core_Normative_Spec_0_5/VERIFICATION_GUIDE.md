# Verification Guide — Spec 0.5

Ejecutar:

```bash
python verify_spec.py
```

El verificador devuelve tres gates independientes.

## CandidateConsistency

Comprueba:
- fuente normativa y hash;
- precedencia exacta;
- catálogo contractual exacto;
- decisiones obligatorias presentes;
- requisitos M0/M2 completos;
- owner/provider/verifier;
- cobertura de tests;
- grafo de fases sin ciclos;
- identidad exacta de los nueve artefactos pre-P01;
- integridad de los archivos listados en manifest;
- coherencia entre estados de decisión y AcceptanceRecord.

No exige que las decisiones ya estén aprobadas.

## SpecApproved

Sólo `YES` cuando:
- CandidateConsistency=PASS;
- las seis decisiones obligatorias están `approved`;
- cada una tiene exactamente un AcceptanceRecord `accepted`;
- el registro apunta a la revisión 0.5 y al hash exacto de la fuente normativa;
- accepted_by, accepted_at y evidence_refs existen;
- no existe contradicción entre decisión y AcceptanceRecord.

Cambiar únicamente el estado en `spec_registry.json` no puede aprobar la Spec.

## PreP01Ready

Sólo `YES` cuando:
- SpecApproved=YES;
- existen los nueve artefactos pre-P01;
- cada archivo tiene hash/revisión;
- cada uno tiene AcceptanceRecord válido;
- el hash del archivo coincide.

## Resultados finales

- `FAIL`: candidata inconsistente.
- `CONSISTENT_DRAFT`: candidata coherente, Spec aún no aprobada.
- `SPEC_APPROVED_NOT_PRE_P01_READY`: diseño aprobado, documentación P00 aún incompleta.
- `PRE_P01_READY`: diseño aprobado y puerta documental completa.

Ningún resultado certifica código, seguridad o integración real.
