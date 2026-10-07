# Revisión de AI OS Core — Especificación normativa 0.6

Fecha: 12 de septiembre de 2026. Alcance: revisión de los catorce archivos de `AI_OS_Core_Normative_Spec_0_6`, contraste con la 0.5 y comprobación de conservación de las reglas señaladas en revisiones anteriores. Sin desarrollo de la aplicación ni elaboración de prompts.

## Dictamen

**La arquitectura y las correcciones de fondo de la 0.6 merecen una valoración favorable.** Los dos problemas prioritarios de la 0.5 están corregidos: se han recuperado las reglas de seguridad y el verificador ya rechaza aceptaciones con dependencias invalidadas o revisiones incompatibles.

**El cierre del paquete queda condicionado a dos correcciones documentales acotadas:** actualizar las referencias que todavía apuntan a 0.5 y sincronizar las listas normativas de hitos con los requisitos añadidos al registro. Son errores comprobados de coherencia, no motivos para rediseñar el sistema ni ampliar su alcance.

Por tanto, distingo dos conclusiones:

- **Diseño y resolución de los problemas anteriores: favorables.** No he identificado en esta revisión un nuevo bloqueo arquitectónico comparable a los de la 0.5.
- **Especificación completamente cerrada y lista para su aprobación: pendiente de T01/T02.** No emito todavía un visto bueno incondicional sobre los archivos tal como están entregados.

Estas correcciones caben en una revisión menor de la entrega. No es necesario volver a analizar desde cero la arquitectura. La aprobación humana y la puerta pre-P01 siguen siendo pasos separados y correctamente declarados como pendientes.

## Comprobaciones realizadas

Se han leído la especificación, ambos registros, catálogo de tests, verificador, autopruebas, manifest, guía, estado del paquete, salidas, changelog y las dos matrices de seguimiento/conservación. Se ha usado como referencia el [informe de la 0.5](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_NORMATIVE_SPEC_AI_OS_CORE_V0_5_2026-09-12.md>).

| Comprobación | Resultado |
|---|---|
| Archivos revisados | 14 |
| Hashes incluidos en el manifest | 10 de 10 coinciden |
| Contratos del texto y del registro | 57, coincidentes |
| Requisitos registrados | 36 |
| Fases | 16 |
| Casos de aceptación documentados en el catálogo | 32 |
| Invariantes obligatorios registrados | 11, presentes en la fuente |
| Requisitos de M0 en el registro | 14 |
| Requisitos de M2-minimal en el registro | 20 |
| Ampliación M2-contextual | 2 requisitos adicionales |
| Grafo y orden proveedor–verificador actuales | Sin discrepancias detectadas |
| Enlaces requisito–test, en ambos sentidos | Coincidentes |
| IDs de requisitos, tests, decisiones e invariantes | Sin duplicados en los datos actuales |

La ejecución real devuelve:

```text
CandidateConsistency: PASS
SpecApproved: NO
PreP01Ready: NO
Errors: 0
Warnings: 1
RESULT: CONSISTENT_DRAFT
```

Las **20 autopruebas suministradas pasan**. También pasan, con el resultado esperado, **cuatro comprobaciones independientes en memoria**:

| Escenario adicional | Resultado observado |
|---|---|
| Decisión aceptada → dependencia aceptada → segunda dependencia aceptada | Permite la aprobación sintética de la spec; mantiene pre-P01 pendiente |
| La segunda dependencia está invalidada | Rechaza la aprobación y detecta la invalidez de los consumidores |
| Cambia el archivo materializado de la segunda dependencia, conservando el hash aceptado anterior | Rechaza la aprobación por diferencia de contenido |
| La segunda dependencia declara compatibilidad con 0.5 | Rechaza la aprobación para 0.6 |

Estos escenarios usan datos de aceptación sintéticos; no representan aprobaciones reales. No se han alterado los registros originales. Las comprobaciones se refieren a la herramienta documental, no a aplicaciones ni integraciones funcionando.

La verificación final de hashes conserva intactos los **122 archivos originales** registrados al iniciar la revisión.

## Seguimiento de los hallazgos de 0.5

| Hallazgo anterior | Evaluación en 0.6 |
|---|---|
| S01. Reglas de acceso y seguridad perdidas | Resuelto: default DENY, techo efectivo, allowlist de servicios y protección de credenciales vuelven a ser normativos |
| S02. Dependencias de aceptación y revisiones | Resuelto en los escenarios señalados y comprobados: referencias, ciclos, validez transitiva, concordancia de revisión/hash y compatibilidad pre-P01 |
| S03. Decisiones anteriores sin destino explícito | Incorporadas las reglas principales y una matriz de conservación; Planner completo y autonomía completa quedan diferidos expresamente |
| S04. Roles, precedencia de fases y cobertura inversa | Resuelto: se prohíbe P10 como proveedor, se exige precedencia y se comprueban ambos sentidos de cobertura |

Las [reglas preservadas](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/NORMATIVE_SPEC_0_6.md:380>) recuperan identidad nativa, revisiones del adaptador, aprobación exacta/por alcance, idempotencia atómica, contexto histórico, dependencias de tareas acíclicas, roles del artefacto y frontera del Planner. La [matriz de conservación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/PRESERVATION_MATRIX_0_4_TO_0_6.md>) permite distinguir conservación, sustitución y diferimiento.

Se mantienen las correcciones anteriores de restore, Policy y autonomía. El contraste textual con la 0.5 muestra adiciones y ajustes de versión, sin una nueva eliminación de sus apartados funcionales. Esto evita la regresión por reducción del texto que motivó la revisión anterior.

La [validación de aceptaciones](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/verify_spec.py:216>) comprueba ahora dependencias por ID, ciclos, aceptación completa, compatibilidad y, cuando hay archivo materializado, su hash. También compara decisión y aceptación. Esta mejora está respaldada por ejecución, no sólo por el changelog.

La guía reconoce además que `covers` y `expected` aportan trazabilidad declarada y que la suficiencia semántica de los tests requiere revisión. Esa limitación es adecuada para una herramienta de esta etapa.

## Correcciones pendientes para cerrar el paquete

### T01 — Media: quedan referencias de versión que contradicen la fuente declarada

**Error comprobado.** El documento afirma ser la única fuente normativa de 0.6, pero la primera entrada de su [precedencia](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/NORMATIVE_SPEC_0_6.md:10>) sigue siendo:

```text
1. NORMATIVE_SPEC_0_5.md
```

En cambio, el [registro](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/spec_registry.json:6>), el manifest y el verificador identifican `NORMATIVE_SPEC_0_6.md`. La intención parece ser 0.6, pero el orden escrito introduce una contradicción precisamente en la regla que debe resolver discrepancias documentales.

Hay otro resto de versión en el [nombre de DOC-CONTRACT-SCHEMAS](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/spec_registry.json:1029>): dice `Contract Schemas 0.5`, mientras que la puerta normativa pide `Contract Schemas 0.6`. La compatibilidad declarada en ese mismo registro sí es 0.6. Por tanto, se trata de una discordancia de denominación; no afirmo que existan esquemas antiguos aceptados.

La lista histórica del apartado 0 también termina en v0.4. Conviene incluir v0.5 para dejar explícito su lugar como antecedente.

**Corrección concreta:** sustituir la referencia principal por 0.6, conciliar el nombre del entregable de esquemas y actualizar el intervalo histórico. No es necesario cambiar la regla de precedencia elegida.

**Cierre verificable:** documento, registro, manifest y verificador identifican la misma fuente actual. Una búsqueda de referencias 0.5 sólo devuelve menciones históricas deliberadas o referencias justificadas.

### T02 — Media: las listas normativas de M0/M2 no se actualizaron con los cinco requisitos nuevos

**Desajuste comprobado.** El registro y las constantes del verificador incorporan los nuevos requisitos, pero el [apartado 14 del texto](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/NORMATIVE_SPEC_0_6.md:505>) conserva las listas anteriores.

| Hito | Requisitos presentes en el registro y ausentes de la lista del apartado 14 |
|---|---|
| M0 | `M0-AUTHORIZATION`, `M0-SERVICE-SECURITY`, `M0-IDENTITY-REVISION` |
| M2-minimal | `M2-TASK-DAG`, `M2-ARTIFACT-ROLES` |

Los [requisitos registrados](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/spec_registry.json:893>) tienen propietario, fases y casos C21–C26. Sus reglas también están en el apartado 13A. **No faltan esas capacidades en el planteamiento general; falta incluirlas en la enumeración que define cuándo se considera completo cada hito.**

Para M0 la diferencia es directa: el texto enumera 11 requisitos y el registro exige 14. En M2, el texto agrupa replay y restore por productor/receptor; esa agrupación puede ser legítima y no la cuento como error por sí misma. Una vez expandida conforme al registro, siguen faltando Task DAG y roles de Artifact.

**Corrección concreta:** incorporar los cinco IDs a sus listas y expresar el mapeo de los dos requisitos agrupados a sus productores/receptores. Mantener las asignaciones actuales, que son coherentes. M2-contextual debe seguir heredando el mínimo y añadir su contexto/replay de KO.

**Cierre verificable:** las listas del documento y los perfiles JSON describen el mismo conjunto, tras aplicar las expansiones declaradas. Quedan 14 requisitos para M0, 20 para M2-minimal y 22 para M2-contextual.

## Por qué el verificador devuelve PASS pese a T01/T02

No hay contradicción en el resultado de ejecución: el verificador comprueba exactamente lo programado. El límite está en qué fuentes compara.

- Para precedencia, compara el valor del JSON con una constante. Lee el Markdown y verifica su hash, pero no extrae la lista de precedencia escrita en él. Véase [source of truth](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/verify_spec.py:76>).
- Para cobertura de hitos, compara los perfiles JSON con conjuntos constantes. No cruza esos conjuntos con las listas del apartado 14. Véase [milestone/profile coverage](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6/verify_spec.py:142>).

Que el hash coincida demuestra qué texto se está revisando; no demuestra que ese texto coincida con los datos estructurados. Ambos errores están presentes en el paquete original y no han requerido introducir ninguna variante artificial para encontrarlos.

Para evitar que reaparezcan, basta una comprobación limitada de esas dos secciones o generar sus listas desde una representación canónica. Si se opta por revisión manual, debe constar expresamente que PASS no compara esas partes del texto. No se necesita un verificador capaz de interpretar automáticamente toda la semántica arquitectónica.

## Recomendaciones de formalización, sin nuevos bloqueos de diseño

- Al preparar el diccionario y las restricciones de persistencia, explicitar la unicidad de `ApprovalUse` por autorización y operación. La distinción exact/scoped está restaurada; conviene conservar también el invariante de reintento sin consumo duplicado que aparecía expresamente en 0.4.
- Mantener los registros de aceptación con referencias a revisiones inmutables. La herramienta comprueba validez transitiva y bloquea estados incoherentes; no sustituye la decisión humana de qué cambio es incompatible ni modifica por sí sola los registros.
- La presencia de un identificador `INV-*` evita ciertas eliminaciones accidentales, pero no garantiza que el texto bajo ese identificador conserve su significado. Mantener la matriz y la revisión semántica de cambios, como propone el paquete.
- En las autopruebas futuras, comprobar también el código de error esperado. Actualmente se busca principalmente el resultado final; distinguir la causa ayuda a evitar que un fallo no relacionado haga pasar una prueba negativa.

Estas recomendaciones no justifican rediseñar la spec ni añadir una nueva ronda de alcance. Pueden incorporarse a su formalización y mantenimiento.

## Condición de cierre

Recomiendo corregir T01/T02 en el paquete, actualizar los hashes afectados y regenerar las salidas del verificador y de sus pruebas. Después basta una comprobación focalizada de esos cambios y de que no alteren las reglas ya revisadas.

**La valoración de fondo es favorable; queda un cierre documental de coherencia, no una revisión arquitectónica pendiente.** Hasta completar ese cierre, el estado `draft-reviewable` sigue siendo adecuado. La aprobación humana real y los entregables pre-P01 se evalúan aparte. No se han preparado prompts ni iniciado desarrollo durante esta revisión.
