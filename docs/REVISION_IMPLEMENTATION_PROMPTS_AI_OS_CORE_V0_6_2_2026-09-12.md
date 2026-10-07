# Revisión del kit de implementación AI OS Core 0.6.2

Fecha: 12 de septiembre de 2026  
Objeto: información y prompts reparados de AI_OS_Core_Implementation_Prompts_0_6_2.  
Referencia normativa: AI OS Core Normative Specification 0.6.1.

## 1. Dictamen

**Favorable como paquete documental de instrucciones, con dos correcciones menores de coherencia.** Los cuatro hallazgos de la revisión anterior quedan resueltos en el contenido del kit. No identifico un bloqueo documental equivalente a los anteriores que obligue a rediseñar o volver a plantear los prompts.

La versión 0.6.2 distingue correctamente la preparación técnica de la aceptación formal, exige cobertura E2E completa y asigna la creación del contexto mínimo a Core antes de verificar el perfil contextual. También impide que P15 invente la política operativa de autonomía.

**Este dictamen no habilita por sí mismo la ejecución.** El paquete normativo canónico devuelve actualmente `SpecApproved: NO` y `PreP01Ready: NO`. El kit recoge correctamente esas condiciones y debe permanecer sujeto a ellas. No se han ejecutado prompts de implementación, desarrollado funciones ni registrado aceptaciones.

## 2. Alcance y comprobaciones

Se ha revisado el kit completo, su diferencia respecto a 0.6.1, las reglas comunes, los requisitos por fase y su correspondencia con la especificación normativa y el informe anterior.

| Elemento | Resultado |
|---|---|
| Archivos del kit | 50 |
| Prompts P00–P15, con P10 dividido en A/B | 17 |
| Diferencias respecto al kit 0.6.1 | 21 archivos añadidos, 22 modificados y 7 sin cambios |
| Referencia a la Spec 0.6.1 y su hash | Presente en los 17 prompts |
| Aplicación del protocolo común de aceptación | Presente en los 17 prompts |
| Entradas de hashes del manifiesto | 48 comprobadas; ninguna discrepancia |
| Copia completa del paquete normativo | 14 archivos, idénticos al paquete canónico actual |
| Verificador documental, paquete canónico y copia incluida | Mismo resultado: consistencia correcta, aceptación pendiente |

El manifiesto principal no incluye su propio archivo ni el manifiesto normativo anidado entre sus 48 entradas. El manifiesto anidado sí se ha contrastado mediante la comparación de los 14 archivos con el paquete canónico. No se ha detectado una discrepancia de contenido.

La base normativa continúa siendo la versión **0.6.1**, con SHA-256:

`d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8`

Que el kit sea 0.6.2 y la especificación siga siendo 0.6.1 es correcto: son versiones de artefactos distintos.

## 3. Cierre de los cuatro hallazgos anteriores

### IP01 — Condiciones de avance y aceptación formal: resuelto

La revisión anterior señalaba que un PASS local, la existencia de documentos o la identificación del Broker podían interpretarse como autorización suficiente para avanzar.

Ahora se exige:

- `CandidateConsistency=PASS` y `SpecApproved=YES` contra el paquete normativo canónico.
- `PreP01Ready=YES` antes de P01; no basta con preparar los nueve documentos.
- Inventario aceptado del servidor Broker antes de P03, con repositorio/ruta, revisión, proceso de entrada, APIs observadas, fecha y AcceptanceRecord vigente.
- Separación entre `TECHNICAL_RESULT` y `GATE_STATUS`, con aceptación formal referenciable.
- Candidatos de aceptación preparados por el agente, sin que este fabrique la aprobación humana.

Fuentes: [prechecks obligatorios](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/PRECHECK_NORMATIVE_GATES.md:5>), [protocolo de cierre](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/PHASE_ACCEPTANCE_PROTOCOL.md:3>), [P00: documentos preparados y aceptación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P00_PRE_P01_DOCUMENTATION.md:37>) y [prerrequisitos de P01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P01_CORE_M0_FOUNDATION.md:19>).

La incorporación del paquete normativo completo también resuelve la entrega incompleta de contexto: incluye registros, catálogo de pruebas, manifiesto y verificador. Además, se aclara que esa copia no sustituye a los registros canónicos cuando sus aceptaciones cambien.

**Conclusión:** el problema de instrucciones queda cerrado. Las aceptaciones pendientes son un estado real previsto por el propio protocolo, no una incoherencia nueva del kit.

### IP02 — Cobertura E2E y herencia de evidencia: resuelto

P10A exige ahora **20 de 20 requisitos satisfechos**. Identificar correctamente una carencia no satisface el requisito. Se distinguen fallos demostrados, verificaciones pendientes y rechazos esperados que sí prueban el comportamiento normativo.

P10B exige **22 de 22 requisitos satisfechos**, mediante una de estas dos modalidades:

- `INHERIT_MINIMAL`: reutilizar evidencia del perfil mínimo con AcceptanceRecord vigente y compatibilidad de contratos, versiones de los servicios, configuración y restricciones de modelo.
- `FULL_22`: comprobar directamente los 22 requisitos.

La evidencia heredada pierde validez si hay cambios incompatibles. Los resultados locales de P02–P08 no sustituyen una aceptación E2E mínima, y comprobar solamente los dos requisitos contextuales no basta para aprobar M2-contextual.

Fuentes: [protocolo E2E](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/E2E_ACCEPTANCE_PROTOCOL.md:3>), [matriz y escenarios de P10A](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P10A_M2_MINIMAL_E2E.md:25>) y [modalidades y aceptación de P10B](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P10B_M2_CONTEXTUAL_E2E.md:19>).

También queda explícito que approvals y presupuesto requieren escenarios que los activen, aunque no intervengan en una operación particular.

**Conclusión:** se cierra la posibilidad documental de confundir diagnóstico con cumplimiento o de aprobar el perfil contextual con cobertura parcial.

### IP03 — Proveedor del ContextPackage antes de P10B: resuelto

P07 incorpora expresamente a Core entre los repositorios afectados y le asigna una capacidad mínima concreta:

- Recibir referencias y revisiones de KO seleccionadas explícitamente.
- Autenticar al principal y aplicar autorización, política y clasificación.
- Validar revisión, hash y copia conservada.
- Crear y persistir un ContextPackage inmutable bajo autoridad de Core.
- Registrar procedencia y exclusiones, y entregar una referencia consumible por Athena.

P04 define a Athena como consumidora del paquete emitido por Core. P07 debe demostrar la ruta KO → Core → Athena → evidencia histórica antes de P10B.

Fuentes: [alcance y proveedor mínimo en P07](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P07_KNOWLEDGE_ORCHESTRATOR.md:16>), [consumo en Athena](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P04_ATHENA.md:25>) y [cierre obligatorio antes de P10B](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P07_KNOWLEDGE_ORCHESTRATOR.md:44>).

La separación con P12 queda bien delimitada: P07 proporciona la capacidad mínima para contexto reproducible; P12 conserva el Context Engine completo, con descubrimiento federado y ranking. P10B verifica una capacidad ya entregada.

**Conclusión:** queda cerrado el hueco de responsabilidad y secuencia. La matriz resumida de repositorios necesita reflejar este cambio, como se indica más abajo.

### IP04 — Definición operativa de autonomía antes de P15: resuelto como condición previa

Se introduce una condición explícita: antes de ejecutar P15 debe existir una definición de política/configuración versionada y aceptada que concrete A0–A5, acciones permitidas, aprobaciones, autoridad para cambiar nivel, promoción, degradación, revocación, métricas y límites de reparación.

P15 queda bloqueado si falta esa definición. La ejecución debe leer sus umbrales y límites de la política aceptada, y la evidencia debe identificar su versión.

Fuentes: [contenido exigido a la política](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/AUTONOMY_POLICY_GATE.md:5>) y [dependencia vinculante de P15](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P15_M6_CONDITIONAL_AUTONOMY.md:19>).

**Conclusión:** el prompt ya no encarga inventar decisiones operativas que la base normativa había dejado pendientes. Esto no significa que la política futura esté ya definida o aceptada; significa que su ausencia se trata correctamente como impedimento previo a P15. No obliga a resolver M6 para comenzar los hitos anteriores cuando sus propias condiciones estén satisfechas.

## 4. Otras reparaciones comprobadas

Las mejoras adicionales refuerzan la correspondencia con la especificación:

- Se explicitan los alias P10A/P10-minimal y P10B/P10-contextual.
- Se recuperan los nombres completos de los contratos de consulta, estado y recibo de operaciones en las instrucciones afectadas.
- P01 amplía la verificación explícita de Goals, Resource Graph, auditoría y casos C23/C24.
- P09 elimina la dependencia imprecisa de un M1 adicional y conserva su carácter opcional.
- P14 exige identificar TypedPlanProposal mediante contrato/esquema versionado, revisión/hash, ejemplos válidos e inválidos y validación por consumidores.
- El manifiesto permite comprobar la integridad de los contenidos listados.

La matriz conserva la distribución de los 14 requisitos M0 entre P01 y P02, los 20 del perfil mínimo y los dos adicionales del contextual. No he encontrado en las reparaciones una transferencia indebida de la autoridad de Tasks, Jobs, contexto o ejecución al componente equivocado.

## 5. Correcciones menores pendientes

### ED01 — Título del README con versión antigua

**Evidencia:** [README, primera línea](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/README.md:1>) identifica el paquete como “Implementation Prompt Kit 0.6.1”, mientras que la carpeta, el manifiesto y KIT_STATUS corresponden al kit 0.6.2.

**Efecto:** puede inducir a identificar incorrectamente la entrega al copiar o distribuir el README.

**Corrección propuesta:** cambiar únicamente la versión del kit en el título a 0.6.2. Mantener las referencias a la Spec 0.6.1, que sí son correctas.

**Gravedad:** baja; no altera los requisitos ni bloquea el dictamen favorable.

### ED02 — Matriz de repositorios sin la participación de Core en P07

**Evidencia:** [fila de Core en la matriz](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/MATRIX_REPO_CHANGES.md:5>) no incluye P07, aunque [P07 declara Core y su capacidad mínima](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_2/prompts/P07_KNOWLEDGE_ORCHESTRATOR.md:16>) sí lo hace.

**Efecto:** una planificación basada exclusivamente en la matriz resumida podría omitir el cambio de Core necesario para entregar el contexto mínimo.

**Corrección propuesta:** añadir P07 a la fila de AI OS Core y mencionar la creación/autorización/persistencia del ContextPackage mínimo. Mantener P12 para el Context Engine completo.

**Gravedad:** baja en esta entrega, porque el prompt operativo define expresamente la responsabilidad, el trabajo y el criterio de cierre. No reabre IP03.

Al realizar estas correcciones conviene recalcular sus entradas en el manifiesto.

## 6. Mejoras opcionales de claridad

Estas mejoras no condicionan el dictamen:

1. **Unificar el formato de salida.** Varios prompts conservan el campo antiguo `PHASE_RESULT` junto a `TECHNICAL_RESULT` y `GATE_STATUS`. El protocolo común ya establece la separación correcta; eliminar el campo redundante o definirlo como resumen evitaría resultados contradictorios.
2. **Hacer explícita la recepción de la aceptación en P10A.** Donde se indica “preparar/solicitar AcceptanceRecord…; sólo entonces GATE_STATUS=ACCEPTED”, usar “sólo cuando exista AcceptanceRecord vigente”. El protocolo común ya impone esta condición, pero repetirla con la misma redacción evitaría que una lectura aislada confundiera solicitud con aceptación.

No es necesario introducir nuevas capacidades de producto para aplicar estas mejoras.

## 7. Estado actual de las condiciones normativas

Se ha ejecutado el verificador documental tanto en el paquete normativo canónico como en la copia incluida. Ambos devuelven:

```text
CandidateConsistency: PASS
SpecApproved: NO
PreP01Ready: NO
Errors: 0
Warnings: 1
RESULT: CONSISTENT_DRAFT
```

La advertencia GATE001 indica que las decisiones/aceptaciones todavía no habilitan SPEC_APPROVED. No es un error de consistencia de los contenidos.

Por tanto:

| Pregunta | Respuesta |
|---|---|
| ¿Las reparaciones responden a los cuatro hallazgos anteriores? | Sí, documentalmente. |
| ¿El kit puede recibir un informe técnico favorable? | Sí, con los ajustes menores descritos. |
| ¿La especificación está formalmente aprobada según su registro actual? | No. |
| ¿P01 está habilitado actualmente? | No. |
| ¿Este análisis demuestra que los servicios o E2E funcionan? | No; esas pruebas corresponden a la futura implementación. |

## 8. Alcance del resultado

El resultado acredita coherencia documental y cierre de los problemas detectados en el kit anterior. La comprobación automática realizada valida el paquete normativo y la integridad de archivos; no ejecuta la aplicación ni demuestra cumplimiento operativo.

Se entrega únicamente este informe. Las especificaciones, los prompts y los registros de aceptación originales se mantienen sin modificaciones.

