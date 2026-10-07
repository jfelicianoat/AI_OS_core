# Revisión de AI OS Core — Especificación normativa 0.6.1

Fecha: 12 de septiembre de 2026. Alcance: revisión documental de los catorce archivos del paquete 0.6.1, comprobación focalizada de T01/T02 y contraste de conservación respecto a la 0.6. Sin desarrollo de la aplicación ni elaboración de prompts.

## Dictamen

**Dictamen documental positivo. La 0.6.1 resuelve los dos pendientes de la revisión anterior y conserva el diseño ya valorado favorablemente.** No he identificado nuevos errores que impidan cerrar esta revisión de especificaciones.

La fuente normativa, el registro, los perfiles de hitos y los nombres de los entregables están conciliados. El verificador incorpora comprobaciones concretas para detectar las divergencias que motivaron T01/T02, y sus pruebas se ejecutan correctamente.

**Considero cerrados T01 y T02. No solicito otra versión correctiva para continuar con el análisis de los prompts que aporte el usuario.** La especificación 0.6.1 puede utilizarse como referencia de esa revisión.

Este dictamen evalúa la calidad y coherencia documental. La aceptación humana registrada y la preparación para iniciar P01 son estados distintos que el propio paquete mantiene pendientes. No se han modificado esos estados ni se ha iniciado desarrollo.

## Comprobaciones y resultados

Se han contrastado los archivos con la 0.6, revisado los cambios del verificador y sus pruebas, ejecutado la validación documental y comprobado los hashes. El punto de partida es el [informe de revisión de la 0.6](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_NORMATIVE_SPEC_AI_OS_CORE_V0_6_2026-09-12.md>).

| Comprobación | Resultado |
|---|---|
| Archivos del paquete revisados mediante lectura y contraste | 14 |
| Hashes incluidos en el manifest | 10 de 10 coinciden |
| Contratos canónicos | 57; texto y registro coinciden |
| Requisitos registrados | 36 |
| Fases | 16 |
| Casos de aceptación del catálogo | 32 |
| Invariantes obligatorios | 11, conservados |
| M0 | 14 requisitos, iguales en texto y registro |
| M2-minimal | 20 requisitos, iguales en texto y registro |
| M2-contextual | Hereda los 20 y añade 2; total 22 |
| Duplicados en las listas normativas de los perfiles | Ninguno |
| Autopruebas del verificador | 24 de 24 pasan |

La ejecución real produce:

```text
CandidateConsistency: PASS
SpecApproved: NO
PreP01Ready: NO
Errors: 0
Warnings: 1
RESULT: CONSISTENT_DRAFT
```

La advertencia corresponde a las decisiones/aceptaciones todavía pendientes. No señala una incoherencia nueva de la candidata.

Las 24 autopruebas comprueban la herramienta documental. No deben confundirse con los 32 escenarios de aceptación del producto descritos en el catálogo: estos últimos no se han implementado ni ejecutado durante esta revisión.

La comparación final de hashes conserva intactos los **137 archivos originales** registrados al comenzar el trabajo.

## T01 — Referencias de versión: cerrado

La [precedencia escrita](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/NORMATIVE_SPEC_0_6_1.md:8>) identifica `NORMATIVE_SPEC_0_6_1.md`, contratos formales 0.6.1 y los paquetes hasta v0.6 como antecedentes históricos. Coincide con el registro, el manifest y la versión esperada por el verificador.

`DOC-CONTRACT-SCHEMAS` se denomina ahora [Contract Schemas 0.6.1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/spec_registry.json:1029>), en concordancia con la puerta documental. Las referencias de compatibilidad y los hashes de las decisiones y aceptaciones se han actualizado a la nueva fuente.

También se corrige la causa por la que el error anterior pasaba inadvertido: el verificador extrae la lista de precedencia del Markdown y comprueba los nombres de los artefactos. Las nuevas pruebas negativas reproducen la precedencia obsoleta y el nombre antiguo de esquemas, y verifican los códigos `SRC006` y `DOC004`.

**Conclusión:** la contradicción concreta de T01 está resuelta y tiene protección automática frente a su reaparición.

## T02 — Listas de hitos: cerrado

El [apartado 14](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/NORMATIVE_SPEC_0_6_1.md:505>) contiene ahora los requisitos que faltaban:

- M0 incluye autorización, seguridad de servicios e identidad/revisiones.
- M2-minimal incluye dependencias de tareas acíclicas y roles de Artifact.
- Replay y restore se enumeran mediante IDs específicos por productor/receptor.
- M2-contextual declara expresamente la herencia del mínimo y añade evidencia de contexto y replay de KO.

La comparación independiente de las listas no encuentra diferencias con los perfiles JSON. Los rótulos agrupados anteriores quedan identificados como descripciones conceptuales, sin sustituir a los requisitos normativos expandidos.

El verificador compara ahora estas listas del Markdown con los conjuntos esperados mediante `MIL005`, `MIL006` y `MIL007`. Las nuevas autopruebas de eliminación de un requisito de M0 y otro de M2-minimal comprueban además el código de error concreto, tal como se recomendó.

**Conclusión:** las condiciones de cierre de los hitos se describen de forma consistente en el texto y en el registro.

## Conservación de las correcciones anteriores

El contraste muestra que el parche se limita a sincronización documental, referencias de versión y comprobaciones del verificador. No introduce cambios funcionales en ownership, Policy, aprobaciones, eventos, restore, certificación, scheduling, frontera del Planner o autonomía.

En particular:

- Los requisitos, fases e invariantes del registro mantienen su contenido funcional.
- El catálogo de aceptación conserva sus escenarios; cambia su identificación de versión.
- Las aceptaciones mantienen sus estados pendientes y dependencias declaradas; se actualiza su vinculación a la nueva revisión.
- La matriz de conservación mantiene las reglas y diferimientos de la 0.6.
- Las veinte autopruebas anteriores siguen pasando junto a las cuatro nuevas, incluidas las relativas a invalidación, revisiones incompatibles, dependencias inexistentes/circulares, roles de fases y cobertura inversa.

Por ello, no se reabren los problemas de seguridad y aceptación transitiva ya resueltos en la 0.6.

## Observaciones menores y alcance del cierre

No quedan hallazgos bloqueantes en esta revisión focalizada. Como detalle editorial opcional, el apartado 13A conserva la frase «normativos en 0.6» para los invariantes heredados. Puede armonizarse con «en esta versión» en una edición posterior; el apartado sigue dentro de la fuente vigente y no modifica la precedencia ni contradice las reglas preservadas. No requiere otra ronda correctiva.

La [guía de verificación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/VERIFICATION_GUIDE.md>) delimita correctamente sus comprobaciones de estructura y trazabilidad. Un resultado favorable no demuestra comportamiento de servicios reales ni suficiencia de todas las futuras implementaciones. La formalización de contratos, matrices, transiciones y fixtures sigue correspondiendo a los entregables pre-P01 previstos.

| Estado | Resultado de esta revisión |
|---|---|
| Calidad y coherencia documental de la candidata | **Favorable; revisión cerrada** |
| Aceptación humana registrada de las seis decisiones | Pendiente, tal como declara el paquete |
| Puerta documental pre-P01 | Pendiente, tal como declara el paquete |
| Inicio de desarrollo | No realizado |
| Revisión de futuros prompts aportados por el usuario | Puede tomar esta especificación como referencia |

## Referencia exacta revisada

Fuente: [NORMATIVE_SPEC_0_6_1.md](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/NORMATIVE_SPEC_0_6_1.md>).

SHA-256:

```text
d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8
```

El dictamen positivo corresponde a esta revisión y al paquete comprobado. Los próximos prompts deberán conservar sus responsabilidades, restricciones y puertas documentales; su análisis será una revisión separada.
