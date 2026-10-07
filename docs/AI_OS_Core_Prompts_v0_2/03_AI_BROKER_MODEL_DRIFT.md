# Prompt 03 — AI Broker + Model Drift: identidad, comparabilidad y certificación manual

## FASE ARQUITECTÓNICA
OS-2 integración base.

## PRERREQUISITOS
Core prompts 01–02.
Identificar el repositorio servidor real de AI Broker antes de modificarlo.

# A. AI BROKER

## INVENTARIO PRIMERO
Contrastar API real actual. Tratar “cambio mínimo” como hipótesis.

## EXPONER
### Model identity evidence
Por componente:
- value;
- evidence_status: verified / declared / unavailable;
- evidence_source;
- observed_at.

No colapsar toda la identidad en un hash.

### Stable index hash opcional
Si se usa:
- JSON canonicalizado;
- lista de campos incluida;
- excluir timestamps/observed_at;
- hash no equivale a prueba de identidad.

### Capacity observation
Snapshot con unidades definidas.

### Historical duration evidence
P50/P80/P95 sólo si hay muestra suficiente; publicar:
- sample_count;
- window;
- workload signature;
- uncertainty/confidence.
Si no hay historial: `insufficient_data`.

### model lifecycle
Eventos versionados con `source_sequence` y `resource_revision`.

# B. MODEL DRIFT

## NO PERDER SU MODELO DE EVIDENCIA
Conservar:
- capas de identidad;
- estado por componente;
- procedencia;
- comparabilidad parcial.

Separar:
1. `EvaluationVerdict` histórico.
2. `Certification` histórica.
3. `CertificationApplicability` frente al candidato actual.

Una certificación histórica nunca cambia a FAILED porque cambie el candidato.

Estados de aplicabilidad:
- applicable
- stale
- not_applicable
- indeterminate

## CERTIFICACIÓN MANUAL EN ESTA FASE
Añadir contratos y ejecución manual de suite.
La automatización por evento queda para Prompt 11.

## PRUEBAS
- dato antes unavailable pasa a declared sin asumir model changed;
- dos fingerprints con críticos desconocidos => identidad no demostrada;
- certificación histórica permanece intacta;
- aplicabilidad cambia por skill/runtime/model/tool/policy revision.
