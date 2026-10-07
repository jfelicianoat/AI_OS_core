# Revisión de AI OS Core — Prompts de implementación 0.6.1

Fecha: 12 de septiembre de 2026. Alcance: los 29 archivos de `Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1`, incluidos sus 17 prompts, contrastados con la especificación normativa 0.6.1 y sus registros originales. No se han ejecutado los prompts ni iniciado desarrollo.

## Dictamen

**El kit está bien orientado y respeta en general la arquitectura aprobable de la 0.6.1, pero todavía no lo considero completamente cerrado como conjunto de instrucciones ejecutables.** Las responsabilidades, las restricciones principales y los conjuntos de requisitos están bien trasladados. Los pendientes se concentran en cómo se demuestra la aceptación de una fase, cómo se hereda la evidencia E2E y quién entrega la parte mínima de contexto del Core antes de M2-contextual.

Hay **dos hallazgos de prioridad alta y dos de prioridad media**. Los primeros afectan a las condiciones para avanzar y al significado de completar M2. Los medios afectan a la integración contextual y a la concreción previa de P15. No justifican rediseñar la arquitectura ni reabrir el dictamen documental positivo de la especificación.

**Valoración:** conforme en orientación arquitectónica y cobertura declarada; pendiente de ajustes de ejecución y aceptación. Recomiendo corregirlos antes de usar el kit para encadenar fases automáticamente.

## Comprobaciones realizadas

| Comprobación | Resultado |
|---|---|
| Archivos revisados | 29: 8 generales, 17 prompts y 4 referencias |
| Prompts declarados en el manifest | 17; todos existen, sin entradas repetidas |
| Estructura de los prompts | Los 17 comparten las mismas 13 secciones |
| Baseline incluida en cada prompt | Los 17 citan la versión y el hash correctos |
| Copias de referencia | Las 4 son idénticas a las del paquete normativo original |
| Requisitos M0 de la matriz | 14; coinciden con el registro normativo |
| Requisitos M2-minimal de la matriz | 20; coinciden con el registro normativo |
| Ampliación M2-contextual | 2, heredando los 20 del mínimo |
| Archivos originales conservados | 167; sin cambios en la comprobación final de hashes |

La copia de `NORMATIVE_SPEC_0_6_1.md` tiene el SHA-256 correcto:

```text
d98f9a21c2de1df9b703350acf3434dbf597d13f73fc4bc2a02d78c48793eca8
```

Se ha vuelto a ejecutar únicamente el verificador documental del paquete normativo original. Su resultado actual es:

```text
CandidateConsistency: PASS
SpecApproved: NO
PreP01Ready: NO
RESULT: CONSISTENT_DRAFT
```

Las seis decisiones continúan `proposed`. Esto no invalida el [dictamen documental positivo de la especificación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_NORMATIVE_SPEC_AI_OS_CORE_V0_6_1_2026-09-12.md>); confirma que valoración técnica y aceptación formal registrada son estados distintos.

No se han inspeccionado los repositorios de las aplicaciones para certificar sus APIs actuales. El kit exige hacerlo al comenzar cada fase, lo cual es adecuado. Este informe evalúa las instrucciones y su correspondencia documental, no la viabilidad demostrada de integraciones que todavía no se han ejecutado.

## Aspectos que cumplen bien

- La baseline está fijada por hash y los prompts exigen informar de incompatibilidades mediante `SPEC_GAP_REPORT`, en lugar de adaptar silenciosamente la arquitectura al código existente.
- Se mantienen las autoridades: Core para control y contexto; Gestión Tareas para planificación y calendario; Agora para Jobs y admisión de workers; Broker para inferencia; Athena para ejecución y permisos; Model Drift para evaluación/certificación; KO para conocimiento; ChatyGPT para UI.
- P02 entrega Policy base, approvals, presupuesto, autorización y proyección de certificación. No se difieren esas funciones mínimas a P13 o P11.
- P03 incorpora enforcement de modelos, evidencia efectiva, admisión, replay y restore. P04 conserva los permisos de Athena y no convierte una aprobación del Core en elevación de privilegios.
- Se preservan IDs nativos, idempotencia, separación entre admisiones, restricciones de eventos, contexto histórico, DAG de tareas y roles de Artifact.
- P10 verifica y remite las funciones ausentes a su proveedor; no se le encarga completar la aplicación durante el E2E.
- P07 es opcional para M2-minimal y P09 no debe convertirse en dependencia crítica.
- P14 mantiene el Planner como productor de propuestas tipadas y solicita Tasks a Gestión Tareas; Core no crea Jobs directamente.

No considero un defecto que los prompts sean concisos o remitan a la spec. El problema aparece cuando sus criterios locales de cierre no expresan una condición normativa indispensable o cuando una responsabilidad compartida queda sin entrega asignada.

## Evaluación por prompt

| Prompt | Evaluación |
|---|---|
| P00 | Enumera correctamente los nueve artefactos y mantiene el trabajo documental; debe completar su cierre con aceptaciones vigentes y resultado pre-P01 |
| P01 | Alcance M0 coherente; el prerrequisito `P00 PASS` necesita equivalencia explícita con la puerta normativa |
| P02 | Buena correspondencia con las cinco obligaciones M0 asignadas; casos de Policy, approvals, presupuesto y clasificación incluidos |
| P03 | Bien situado antes del E2E; falta exigir expresamente la aceptación del inventario del Broker y normalizar nombres de restore |
| P04 | Respeta PermissionEngine, modelo efectivo y replay; precisar la conexión del hook de contexto con el paquete autorizado del Core |
| P05 | Coherente en Job, binding, WorkerAdmission y recuperación; normalizar nombres de contratos de restore |
| P06 | Coherente en Task→Job, segmentos humanos, DAG, agregación y previsiones; mantiene calendario separado de cómputo |
| P07 | Bien definido el suministro de evidencia por KO; falta asignar expresamente la parte del Core para el perfil contextual |
| P08 | UI y autorización del servidor bien separadas; la evidencia real completa queda para el E2E |
| P09 | Puede mantenerse opcional; aclarar el prerrequisito «M1 Core», que no tiene cierre definido en este kit |
| P10A | Buen alcance de verificación; el criterio «evidencia o un fallo atribuido» no define suficientemente qué permite PASS |
| P10B | Debe heredar evidencia mínima vigente o verificarla completa, además de sus dos requisitos propios |
| P11 | Respeta la distinción entre gate manual previo y automatización; conservar requisitos formales de aceptación al promover fase |
| P12 | Flujo general coherente para Context Engine; no debe ser el primer proveedor de la función mínima requerida por P10B |
| P13 | Expansión razonable de P02; no debe usarse para posponer combinaciones obligatorias de Policy que ya pertenecen a M0 |
| P14 | Respeta la frontera del Planner y la revisión humana inicial; concretar su contrato en los entregables previstos |
| P15 | Preserva los gates, pero la semántica operativa de niveles/promoción/repair requiere definición previa a su activación |

## Hallazgos pendientes

### IP01 — Alta: falta convertir las puertas normativas en condiciones verificables de los prompts

La [spec](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/NORMATIVE_SPEC_0_6_1.md:768>) distingue aprobación de la spec, preparación pre-P01 e identificación aceptada del Broker. También exige [AcceptanceRecord](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_6_1/NORMATIVE_SPEC_0_6_1.md:573>) para decisiones, contratos, hitos y artefactos.

El kit menciona estos conceptos de forma incompleta:

- [P00](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P00_PRE_P01_DOCUMENTATION.md:16>) presupone una spec aprobada para derivación, pero no indica cómo comprobar el estado registrado. Sus criterios de aceptación se limitan a existencia de los nueve artefactos y ausencia de decisiones M0 implícitas de alta prioridad.
- [P01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P01_CORE_M0_FOUNDATION.md:16>) exige sólo `P00 PASS`. No declara que PASS requiera aceptaciones vigentes por revisión/hash y `PreP01Ready=YES`.
- [P03](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P03_BROKER_MODEL_DRIFT.md:16>) pide identificar repo/ref/commit del Broker, pero no su aceptación en inventario, exigida por la spec.
- Los formatos de salida incluyen `PHASE_RESULT`, pero no una regla general para registrar y reutilizar aceptaciones vigentes de contratos e hitos.

La lectura obligatoria de la spec sigue imponiendo esas condiciones: no afirmo que los prompts ordenen saltárselas. La debilidad es que el criterio local de PASS puede parecer satisfecho antes de cumplir la puerta normativa.

Además, `reference/` no contiene `spec_registry.json`, `test_catalog.json`, `acceptance_registry.json`, el manifest normativo ni `verify_spec.py`. La guía copiada remite a ese verificador, pero el kit no define una ruta al paquete completo. El `manifest.json` del kit enumera prompts y no sustituye al manifest normativo. Los archivos existen en el paquete hermano del workspace, pero esa dependencia debe quedar explícita para ejecutar o trasladar el kit.

**Corrección:** establecer una precomprobación común con la ubicación del paquete normativo completo, hash y resultados de sus puertas. P00 debe distinguir «documentos preparados» de «documentos aceptados». P01 sólo avanza con `PreP01Ready=YES`; P03, con inventario del Broker aceptado. Registrar aceptación de los hitos y contratos afectados, con revisión, evidencia y dependencias, sin fabricar aprobaciones humanas.

**Cierre verificable:** nueve documentos existentes pero no aceptados no habilitan P01. Un reporte positivo del agente no sustituye una AcceptanceRecord vigente. Si la aprobación ya existe en otro lugar, se incorpora su referencia verificable; no se solicita de nuevo innecesariamente.

### IP02 — Alta: el cierre E2E y la herencia del perfil contextual necesitan reglas inequívocas

Hay dos puntos relacionados:

**P10A no separa suficientemente informe completo y hito superado.** Su [criterio de aceptación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P10A_M2_MINIMAL_E2E.md:37>) dice que los 20 requisitos deben tener «evidencia o un fallo atribuido a provider phase». Atribuir un fallo completa el diagnóstico, pero no satisface el requisito. `PHASE_RESULT` no tiene aquí una regla que impida PASS cuando falta una función o una prueba necesaria.

**P10B puede cumplir sus prerrequisitos sin evidencia del mínimo.** Exige [P02–P08 PASS](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P10B_M2_CONTEXTUAL_E2E.md:16>), pero su tarea y sus pruebas se centran en los dos requisitos adicionales de KO/contexto. No exige P10A aceptado ni ordena volver a verificar los 20 requisitos mínimos. El orden recomendado sitúa P10A antes, pero no define una dependencia de aceptación que pueda comprobarse al ejecutar P10B por separado.

**Ejemplo:** P02–P08 pasan sus pruebas locales, P10A no se ha ejecutado y P10B demuestra C12 y replay de KO. Hay evidencia de los dos requisitos nuevos, pero no del E2E completo de 22 requisitos. No sería suficiente para promover M2-contextual.

**Corrección:** definir PASS sólo cuando todos los requisitos obligatorios del perfil tienen evidencia satisfactoria y vigente. Una función ausente o una prueba requerida sin ejecutar deja el resultado como FAIL/BLOCKED o equivalente; un rechazo esperado demostrado por un test negativo sí cuenta como evidencia satisfactoria.

Para P10B hay dos opciones válidas: consumir una aceptación M2-minimal vigente y añadir los dos requisitos, o ejecutar y acreditar los 22 en esa fase. La primera opción debe vincular la evidencia mínima a las revisiones de contratos, builds y configuración pertinentes; cambios incompatibles obligan a revalidarla.

Los «si aplica» de approvals/budget en el escenario de P10A deben referirse a cada operación, no excluir esos requisitos del hito. Incluir escenarios que activen y comprueben las obligaciones cuando correspondan.

**Cierre verificable:** un informe con un requisito pendiente no promueve M2; P10B entrega referencias verificables a evidencia de los 22 requisitos, propia o heredada válidamente.

### IP03 — Media: falta asignar la entrega mínima del Core para M2-contextual

**Laguna de asignación, no fallo de software demostrado.** La spec atribuye `ContextPackage` al Core y el registro incluye a KO, Athena y Core como propietarios participantes en `M2-CONTEXT-EVIDENCE`, con proveedores P07/P04.

En el kit, [P04](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P04_ATHENA.md:22>) añade un hook de evidencia en Athena y [P07](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P07_KNOWLEDGE_ORCHESTRATOR.md:22>) suministra referencias, snapshots y metadatos desde KO. Sus repositorios afectados se limitan a esas aplicaciones. La construcción del paquete federado se encarga expresamente al Core en P12, posterior al M2-contextual que P10B debe verificar.

Un hook consumidor y una fuente de evidencia no concretan quién produce, autoriza y vincula el paquete mínimo al Run bajo autoridad del Core. Podría resolverse con una entrega pequeña previa o con una capacidad ya existente, pero ninguna de las dos queda identificada como condición de cierre.

**Corrección:** asignar a P04/P07 la contribución mínima del Core, indicando repositorio, interfaz y evidencia de aceptación; si existe previamente, referenciar su contrato y comprobación. Basta un flujo manual de paquete autorizado y reproducible que Athena consuma. No se necesita adelantar ranking global ni el Context Engine completo de P12.

**Cierre verificable:** antes de P10B está descrita y entregada la ruta KO → paquete bajo autoridad del Core → consumo Athena → evidencia histórica exacta del Run. P10B sólo verifica esa ruta; no tiene que construirla.

### IP04 — Media, antes de P15: la autonomía completa aún necesita su definición operativa

La 0.6.1 define el mínimo de autonomía: orden de gates, techo A0–A5, motivos de bloqueo y A0 como observación. La matriz de conservación difiere expresamente la autonomía completa a M6.

[P15](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/Prompts desarrollo/AI_OS_Core_Implementation_Prompts_0_6_1/prompts/P15_M6_CONDITIONAL_AUTONOMY.md:22>) pide promoción «explícita y medible» y `A5 repair` con límites, pero no identifica una definición aceptada de A1–A5, transiciones de promoción/degradación, métricas, umbrales ni reglas concretas de reparación/escalado. La baseline no convierte automáticamente esas decisiones diferidas en decisiones resueltas.

Los límites conservadores del prompt son útiles. No obstante, un agente tendría que elegir parte del significado operativo de los niveles, no sólo implementar un contrato existente.

**Corrección:** mantener P15 como fase condicionada a una política de autonomía aceptada, con niveles, acciones permitidas, promoción/degradación, límites de reparación y criterios de parada. Los valores pueden ser configurables; su interpretación y la autoridad que los aprueba deben estar definidas antes de activarla.

**Cierre verificable:** el agente ejecuta una política identificada y versionada; no inventa el significado de A1–A5 ni las condiciones para ampliar autonomía. Esto no bloquea P00–P10 una vez resueltos sus propios pendientes.

## Ajustes menores de precisión

- Usar los nombres canónicos completos `OperationStatusQuery`, `OperationExecutionStatus` y `OperationReceipt` en P01/P03/P05. `OperationStatus`, `ExecutionStatus` o `Receipt` pueden entenderse como abreviaturas, pero no deben acabar generando contratos nuevos.
- Añadir una tabla explícita `P10A → P10-minimal` y `P10B → P10-contextual` para cruzar prompts, registro y evidencias sin inferir alias.
- Referenciar `M0-GOALS`, `M0-GRAPH`, `M0-AUDIT`, C23 y C24 por su ID exacto en P01. Su descripción general está presente; el ajuste facilita comprobar cobertura contra el catálogo.
- Aclarar el prerequisito «M1 Core» de P09 y su lugar opcional en EXECUTION_ORDER. No debe convertirse en una puerta indefinida ni bloquear M2.
- El manifest fija la spec y enumera prompts, pero no fija el contenido de cada prompt por hash. Añadir revisión/hashes del kit ayudaría a demostrar qué instrucciones originaron cada entrega; no es una exigencia de firma criptográfica ni un motivo para cambiar la arquitectura.

## Qué corregir antes de ejecutar y qué puede esperar

| Momento | Ajuste necesario |
|---|---|
| Antes de dar por habilitado el kit | Localizar la aceptación formal de la spec y las referencias normativas completas |
| Antes de P01 | Convertir el cierre de P00 en aceptación pre-P01 verificable |
| Antes de P03 | Aceptación del inventario del servidor Broker |
| Antes de P10A/P10B | Definir PASS, evidencia por requisito y herencia válida del mínimo |
| Antes de M2-contextual | Asignar la entrega mínima del Core para contexto |
| Antes de P15 | Política operativa de autonomía aceptada |

El kit no necesita una reescritura completa. Conviene conservar su estructura, baseline y reparto de fases, completar estas condiciones y añadir trazabilidad requisito → prompt proveedor → verificador → evidencia/aceptación. **La especificación mantiene su dictamen positivo; el conjunto de prompts requiere estos ajustes para merecer el mismo dictamen como procedimiento ejecutable.**
