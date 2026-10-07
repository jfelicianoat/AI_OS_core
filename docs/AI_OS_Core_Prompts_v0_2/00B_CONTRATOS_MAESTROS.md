# Prompt 00B — Contratos maestros y diccionario de datos

## FASE ARQUITECTÓNICA
OS-0.

## PRERREQUISITOS
`00A` aprobado.

## OBJETIVO REAL
Cerrar estructura, obligatoriedad, nulabilidad, formatos, unidades y compatibilidad sin escribir servicio todavía.

## DECISIONES OBLIGATORIAS

### Versiones distintas
No confundir:
- `schema_version`;
- `resource_revision`;
- `capability_version`;
- `skill_version`;
- `service_version`;
- `model_identity`;
- `contract_api_version`.

### Tiempo y duración
- timestamps: RFC 3339 con offset;
- duraciones de transporte: ISO 8601 duration o milisegundos enteros, elegir uno y usarlo siempre;
- unidades de memoria: bytes enteros;
- utilización: rango 0.0–1.0;
- zonas horarias de calendario: IANA TZID.

### Riesgo
Definir R0–R4 de forma normativa, con ejemplos y relación con approval/autonomy.

### Envelope
Decidir si existe un sobre común real. Si existe:
- especificar campos exactos;
- indicar qué contratos lo usan;
- no duplicar `id`/versiones dentro y fuera.

## ENTREGABLES
1. `DATA_DICTIONARY.md`.
2. esquemas JSON/Pydantic conceptuales o JSON Schema **sin lógica de servicio**.
3. fixtures válidos/invalidos por contrato.
4. tabla `campo → obligatorio/null/enum/formato/unidad`.
5. reglas de compatibilidad aditiva pre-1.0.

## RESOURCE REFERENCE
Debe distinguir:
- `global_id`;
- `owner_system`;
- `native_identity`;
- `owner_instance` cuando importe;
- `resource_revision`;
- URI lógica;
- observación.
No exigir migrar IDs nativos.

## HEALTH
Separar:
- `self_health`: healthy/degraded/unhealthy;
- `connectivity_observation`: reachable/unreachable/unknown;
- `registration_lifecycle`: registered/stale/removed.
Definir mapeos, no unificar enums.

## ARTIFACT
Añadir explícitamente:
- autoridad/owner;
- producer;
- custodian/storage owner;
- retention class;
- immutable revision/hash.

## CRITERIOS DE ACEPTACIÓN
- guardar y volver a cargar cada fixture no pierde información;
- `classification_ceiling` y clasificación efectiva quedan definidos;
- `AgentRun.status` tiene enum y transiciones reservadas;
- relaciones del grafo usan sólo vocabulario permitido (`PROVIDES`, no `PROVIDED_BY` salvo que se formalice).
