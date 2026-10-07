# Revisión de AI OS Core — v0.3

Fecha: 12 de septiembre de 2026. Alcance: revisión documental del paquete v0.3, contraste con las dos revisiones anteriores y comprobación de consistencia entre decisiones, contratos, prompts y pruebas previstas.

## Dictamen

**La v0.3 representa un avance real: ya contiene decisiones candidatas concretas, corrige varios errores anteriores y reconoce con precisión lo que todavía no se ha realizado.** La arquitectura sigue siendo defendible. No recomiendo sustituirla ni ampliar el número de componentes.

El paquete todavía necesita algunos ajustes antes de considerarse una especificación cerrada. Los principales problemas restantes son de correspondencia entre documentos y fases: precedencia contradictoria, entregables previos sin asignación completa y pruebas que requieren funciones previstas para más adelante. También quedan reglas operativas por concretar en eventos y aprobaciones.

**Valoración:** buena base para revisar y aprobar decisiones de diseño, pendiente de corregir las incoherencias de este informe y completar la formalización documental P00 antes de iniciar P01. La ausencia actual de código, esquemas o pruebas ejecutadas no es un error del paquete: ahora se reconoce expresamente y concuerda con su estado de borrador.

| Dimensión | Estado |
|---|---|
| Honestidad del estado documental | Corregida respecto a v0.2 |
| Decisiones de arquitectura | Más concretas y, en general, bien orientadas |
| Estructura y organización del kit | Consistente en formato; algunas dependencias incompletas |
| Fuente normativa | Definida, pero con dos órdenes diferentes |
| Contratos | Nombres mejor conciliados; aún no son un inventario completo ni una especificación de datos |
| E2E | Responsabilidades mejor asignadas; quedan discrepancias puntuales |
| Eventos y recuperación | Mejor diseño; faltan garantías para algunos caminos de fallo |
| Preparación para desarrollo | Pendiente de cierre documental, tal como indica el propio paquete |

## Material revisado y alcance de la comprobación

Se han leído los **35 archivos** de v0.3: **16 prompts**, seis decisiones candidatas y los restantes documentos de apoyo. Se han contrastado con los [12 hallazgos de v0.2](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_ANALISIS_AI_OS_CORE_V0_2_2026-09-12.md>) y los temas originales de la [primera revisión](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_ANALISIS_AI_OS_CORE_2026-09-12.md>).

Comprobaciones realizadas:

- El manifest es JSON válido; los 16 prompts enumerados existen y no hay entradas repetidas.
- Los 16 prompts incluyen las mismas 12 secciones, en el mismo orden. La afirmación de estructura homogénea queda respaldada.
- Las seis decisiones `DECISION_*.md` están en estado `proposed`; no se ha encontrado una decisión declarada `approved` dentro de ese conjunto.
- El catálogo canónico tiene 37 entradas y recoge varios cambios de nombre de versiones anteriores.
- Aún no existen `CONTRACT_INVENTORY.md`, `DATA_DICTIONARY.md`, esquemas ni fixtures de contratos en `AI_OS_core/docs`. El changelog lo reconoce; se trata de trabajo previsto, no de una falsa afirmación de entrega.
- Los 49 archivos de entrada registrados al comenzar la revisión v0.2 conservan sus hashes. La nueva versión se ha añadido sin reemplazar silenciosamente los anteriores.
- Se ha vuelto a contrastar la decisión de durabilidad con documentación oficial de SQLite. No se han ejecutado aplicaciones, inferencias, migraciones ni pruebas de producto.

Esta revisión comprueba la calidad y consistencia del análisis. No certifica la integración real de los servicios ni sustituye los ensayos futuros. La identificación del repositorio servidor de AI Broker y el despliegue concreto de Model Drift siguen pendientes y están correctamente señalados como tales.

## Correcciones anteriores que sí están bien incorporadas

### Estado documental y estructura

El [changelog](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/CHANGELOG_v0_3.md:3>) separa decisiones escritas de trabajo no ejecutado. Ya no presenta inventarios, fixtures o integraciones futuras como entregables terminados. La plantilla uniforme se cumple en los 16 prompts. Estas dos correcciones pueden darse por resueltas en su dimensión editorial.

### Políticas y autonomía

La [decisión de políticas](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_POLICY_SEMANTICS.md:35>) distingue permisos, prohibiciones y obligaciones. La obligación `requires_approval` ya no desaparece al combinar `true` con `false`. Se añaden reglas all/any, lógica ternaria y defaults.

La [decisión de autonomía](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_AUTONOMY.md:4>) separa los controles de autorización, certificación y admisión del mínimo entre niveles A0–A5. También distingue acción bloqueada y nivel A0. Corrige el problema de mezclar magnitudes incompatibles.

### Durabilidad

La [decisión SQLite](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_SQLITE_DURABILITY.md:4>) propone una única base transaccional con WAL y FULL, descarta perfiles por tabla y limita sus afirmaciones al entorno real. Es una respuesta adecuada al hallazgo anterior. FULL en WAL añade sincronización al confirmar las transacciones; la configuración y las garantías efectivas deberán verificarse en el despliegue futuro. [Documentación oficial de SQLite](https://www.sqlite.org/pragma.html#pragma_synchronous).

### Aprobaciones y eventos

La [decisión de aprobaciones](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_APPROVAL_MODEL.md:4>) distingue términos inmutables, usos, revocación y estado efectivo. También separa autorización exacta y por alcance. La incoherencia estructural de modificar un grant “inmutable” está corregida.

La [decisión de eventos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_EVENT_DELIVERY.md:14>) permite varios eventos por revisión y distingue snapshot completo, delta, auditoría y notificación. Ya no considera contradictorios todos los payloads distintos de una misma revisión.

### Integración y producto

Se asignan explícitamente Approval API a P02, Task→Job a P05/P06 y enforcement del modelo a P03, antes del E2E. Se separan Core aislado, observación e integración manual; el Planner tiene propietario declarado. El MVP deja de prometer reservas futuras garantizadas de GPU y diferencia previsión de admisión real. Son decisiones razonables que reducen ambigüedad y alcance.

## Seguimiento de la revisión v0.2

“Resuelto como decisión” significa que se ha corregido el planteamiento escrito, no que haya implementación, aprobación humana o pruebas superadas.

| Hallazgo de v0.2 | Estado en v0.3 | Observación |
|---|---|---|
| R01. Changelog confundía instrucciones y resultados | Resuelto en lenguaje; precedencia parcial | Se reconoce el trabajo pendiente, pero README y SOURCE_OF_TRUTH ordenan distinto decisiones y contratos |
| R02. AND genérico en requisitos booleanos | Resuelto como decisión | Combinación por significado y caso C08 explícito |
| R03. Durabilidad por tabla | Resuelto como decisión | Una DB WAL/FULL; sin perfiles por tabla |
| R04. Grant inmutable y consumo mezclados | Resuelto estructuralmente | Autorización/uso/revocación separados; falta completar las carreras y el vínculo con ejecución |
| R05. E2E sin responsables suficientes | Parcialmente resuelto | Puentes y gate tienen responsable; quedan diferencias entre matriz y entregables de P02/P13 |
| R06. Payload distinto en misma revisión | Resuelto en su regla principal | Se permiten varios eventos; falta concretar la aplicación de deltas y cambios de época |
| R07. Nombres inconsistentes | Parcialmente resuelto | Hay catálogo y nombres retirados; algunos tipos usados siguen fuera del catálogo |
| R08. Políticas no deterministas | Avance sustancial | All/any, ternaria y defaults definidos; quedan semánticas de carga/combinación y autoridad presupuestaria |
| R09. Secuencias, reinicios y restauración | Parcialmente resuelto | Epoch, REPLAY_GAP y consulta de recibos; falta cerrar garantías y verificar el caso C15 |
| R10. Plantilla prometida no cumplida | Resuelto en estructura | 16/16 prompts con 12 secciones; “versionados” e impacto de cambios aún necesitan precisión |
| R11. Mínimo entre tipos incompatibles | Resuelto como decisión | Gates separados; mínimo solo sobre A0–A5 |
| R12. MVP/Planner sin fronteras claras | Resuelto en el planteamiento principal | M0/M1/M2 y PlanningService definidos; concretar criterios de cierre por hito |

Respecto a la primera revisión, se conservan mejoras importantes en identidades nativas, evidencia de modelo, contexto reproducible y separación de dominios. La normalización de OS-0/OS-1, los datos obligatorios, transiciones y matrices siguen pendientes de formalización. No vuelvo a contar su ausencia como un error nuevo cuando el paquete reconoce que P00 aún no se ha realizado.

## Observaciones pendientes

Las prioridades califican el documento. **Alta:** resolver antes de utilizarlo como encargo de implementación. **Media:** concretar antes del cierre de la fase afectada. No son defectos demostrados en software ejecutándose.

### V01 — Alta: hay dos órdenes de precedencia documental

**Error comprobado.** El [README](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/README.md:14>) sitúa contratos canónicos antes que decisiones. [SOURCE_OF_TRUTH](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/SOURCE_OF_TRUTH.md:7>) sitúa decisiones antes que contratos. Aunque el README coloca SOURCE_OF_TRUTH en primer lugar y permite resolver el conflicto por esa vía, mantener dos órdenes opuestos vuelve a introducir precisamente la ambigüedad que se pretendía eliminar.

**Mejora:** conservar una única lista normativa y hacer que el README remita a ella sin reproducirla de forma distinta. Aclarar también que una decisión rechazada o sustituida no prevalece por pertenecer a v0.3 y que una propuesta no se convierte en aprobada por su posición en la lista.

**Cierre verificable:** un ejemplo de conflicto contrato/decisión y otro de decisión proposed/approved producen una respuesta inequívoca, con ID y revisión de la fuente que prevalece.

### V02 — Alta: P00 no asigna todos los entregables que las fases siguientes exigen

**Vacío comprobado de planificación.** [P00](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P00_NORMALIZACION_DOCUMENTAL.md:18>) entrega inventario, diccionario, formalización y fixtures. La [checklist previa a P01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/CHECKLIST_CIERRE.md:3>) exige además tablas reales de transiciones y matriz de autorización. [P01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P01_CORE_M0.md:12>) y [P02](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P02_CORE_APPROVALS_POLICIES_BASE.md:12>) las consumen, pero P00 no las asigna expresamente como salidas.

El catálogo canónico tampoco cubre aún todo lo usado: `ModelExecutionConstraint` entra en P03 y `EffectiveExecutionDecision` en P15 sin figurar entre sus 37 entradas. `ContextRequest`, `ServiceRegistration` y `Failure`, presentes en diseños anteriores y relevantes para las APIs propuestas, no están clasificados como retenidos, sustituidos o retirados.

**Mejora:** ampliar las salidas de P00 y su condición de cierre con transiciones, matriz de autorización, reglas de autoridad de eventos y tabla de compatibilidad de nombres. Clasificar cada contrato por fase, estado y productor/consumidor. Una tabla de nombres no sustituye el inventario, y no todas sus entradas necesitan persistencia propia.

**Cierre verificable:** cada entrada requerida por P01/P02/P03 tiene un artefacto concreto que P00 u otra fase previa entrega. No se exige escribir código de producto para resolverlo.

### V03 — Alta: quedan dependencias adelantadas y entregables omitidos dentro del E2E

**Incoherencia comprobada entre pruebas, matriz y prompts.** Hay dos casos claros:

| Caso | Evidencia | Problema |
|---|---|---|
| Reserva concurrente de presupuesto | [P02 exige C06–C09](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P02_CORE_APPROVALS_POLICIES_BASE.md:30>); [C09](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/CRITICAL_ACCEPTANCE_CASES.md:29>) exige reservar 80 sobre 100 de forma excluyente; [P13](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P13_M4_POLICY_ENGINE.md:18>) entrega el protocolo de reservas | P02 no identifica la autoridad ni entrega la reserva real; la decisión solo dice que Policy emite una obligación |
| Consulta/proyección de certificación en Core | [DECISION_E2E_OWNERSHIP](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_E2E_OWNERSHIP.md:13>) la asigna a P03/P02 | P03 entrega certificación manual en Model Drift; los entregables de P02 no incluyen explícitamente consulta/proyección/aplicabilidad de certificación en Core |

**Mejora:** decidir si P02 prueba únicamente la emisión de la obligación mediante un doble de prueba, o si entrega también una autoridad presupuestaria mínima. En el primer caso, no usar esa prueba aislada como evidencia de reserva real antes de P13. Añadir a P02 la consulta/proyección que la matriz le asigna, o reasignarla a otra fase previa a P10.

**Cierre verificable:** cada requisito de M2 tiene productor, consumidor, fase de entrega y prueba apropiada. P10 conserva su papel de verificación y no incorpora funciones nuevas de forma implícita.

### V04 — Alta: “outbox con el cambio local cuando sea posible” deja una garantía esencial abierta

**Vacío de especificación.** La [decisión de eventos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_EVENT_DELIVERY.md:25>) exige persistir outbox con el cambio local “cuando sea posible”. Si un productor guarda el cambio y cae antes de guardar el evento, el Core no podrá recuperarlo únicamente reproduciendo esa outbox. Esto importa en un ecosistema con persistencias distintas y adaptadores.

La v0.2 sí describía explícitamente escritura de negocio más evento local, y efecto del handler más marcado de procesamiento, como unidades atómicas. La v0.3 no las desarrolla con el mismo detalle. Su menor extensión no las deroga necesariamente, pero tampoco conviene que una garantía crítica dependa de rescatar instrucciones históricas.

**Mejora:** conservar las invariantes transaccionales en la fuente actual. Para productores donde la atomicidad no sea posible, elegir y documentar otro mecanismo recuperable o declarar una garantía más limitada. Una reconciliación de estado puede recuperar el estado final sin recuperar todos los hechos intermedios de auditoría: esas garantías deben distinguirse.

**Cierre verificable:** el caso «cambio persistido, caída antes de crear/publicar evento» tiene resultado esperado, mecanismo de recuperación y límite reconocido para cada productor. Hacer lo mismo con efecto de handler persistido antes del marcado como procesado.

### V05 — Media: permitir deltas requiere definir su base y su orden de aplicación

**Vacío de especificación.** Separar `full_state`, `delta`, `audit` y `notification` corrige la falsa contradicción entre payloads. Sin embargo, la [decisión de entrega](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_EVENT_DELIVERY.md:10>) no define sobre qué revisión se aplica cada delta, cuándo se puede avanzar la proyección ni cómo se ordenan épocas distintas.

Ejemplo: un cambio de estado en revisión 8 y la incorporación de un artefacto en revisión 9 llegan desordenados. Si se aplica el segundo delta a una base anterior y se descarta después la revisión 8 por ser más antigua, la proyección puede conservar un estado incompleto. La secuencia permite detectar un hueco, pero hace falta decidir qué se procesa mientras se recupera.

**Mejora:** exigir una revisión base para deltas, o garantizar y describir aplicación ordenada antes de avanzar la proyección. Definir espera/replay/snapshot, punto de reanudación y tratamiento de eventos de una época anterior que lleguen tarde. Para `adapter_revision`, indicar quién la asigna, cuándo persiste y cómo evita que distintas observaciones del mismo recurso inventen órdenes incompatibles.

**Cierre verificable:** un caso con dos deltas fuera de orden y otro con un evento tardío de una época previa terminan en el estado correcto sin descartar un cambio necesario. Si el MVP solo acepta snapshots para proyectar estado, declararlo simplifica esta decisión.

### V06 — Media: falta cerrar la relación entre uso de aprobación y ejecución efectiva

**Vacío de especificación, no repetición del error de inmutabilidad.** La separación de entidades es correcta. [ApprovalUse](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_APPROVAL_MODEL.md:18>) tiene unicidad por autorización/operación y el texto exige comprobar expiración/revocación transaccionalmente. Falta precisar en esa misma operación el control de `max_uses`, validación del predicado/digest y registro de la orden que se ejecutará.

Ejemplos pendientes: dos operaciones diferentes compiten por el último uso; una operación reutiliza su ID con otro digest; se consume el uso y el servicio cae antes de enviar la orden; la autorización vence o se revoca entre ese consumo y el inicio efectivo en otro sistema.

**Mejora:** definir el punto en que una operación queda autorizada y comprometida, qué puede hacer un reintento y qué revoca una decisión posterior. Mantener un vínculo durable entre uso y comando; no interpretar un uso registrado como prueba de ejecución. La condición de unicidad evita repetir el mismo uso, pero no sustituye el control atómico del límite total ni la igualdad de la acción en un reintento.

**Cierre verificable:** dos solicitudes concurrentes con un solo uso restante no obtienen ambas autorización; un ID reutilizado con acción distinta se rechaza; un reinicio no pierde la orden ni provoca una segunda ejecución. Son resultados a documentar antes de programar, no pruebas realizadas en esta revisión.

### V07 — Media: el caso de restauración C15 no tiene verificación asignada

**Omisión comprobada.** [C15](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/CRITICAL_ACCEPTANCE_CASES.md:47>) exige consultar el recibo para no repetir una operación ya ejecutada. Ninguno de los 16 prompts lo referencia expresamente. [P10](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P10_M2_E2E_MANUAL.md:24>) reutiliza C01–C14 y enumera outage/replay, pero no restauración de una copia anterior.

Restaurar una copia antigua no equivale a reiniciar la última base: puede haber desaparecido el registro local de operaciones cuyos efectos externos ya ocurrieron. La decisión SQLite añade una salida adecuada, `manual_reconciliation_required`, si no puede determinarse el resultado; ese camino tampoco tiene caso de aceptación asignado.

**Mejora:** asignar C15 y la variante sin recibo a una fase de recuperación concreta y a una puerta de cierre. Precisar quién ofrece/retiene el recibo, qué resultado significa “desconocido” y cuándo se permite reenviar. Diferenciar explícitamente pruebas aisladas, con receptor simulado, y evidencia real de los receptores utilizados.

**Cierre verificable:** restore más replay no repite una operación confirmada externamente, y un resultado incierto bloquea el reenvío automático según la decisión adoptada.

### V08 — Media: la plantilla uniforme no garantiza todavía control de versiones e impacto

**Mejora documental pendiente.** Las 12 secciones sí existen en todos los prompts; el defecto de estructura anterior está resuelto. El contenido de “prerrequisitos versionados” sigue usando a menudo `P03 disponible`, `P01` o `M2 cerrado`, sin identificar revisión aceptada, evidencia ni artefactos concretos. Esto puede resolverse mediante un registro compartido; no requiere repetir hashes manualmente en cada párrafo.

Además, P08, P11 y P15 indican “No aplica” en artefactos a reabrir si cambia una decisión, pese a depender de contratos de API, certificación, políticas y aprobaciones. Véanse [P08](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P08_CHATYGPT_M1_M2.md:36>), [P11](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P11_M3_AUTO_CERTIFICATION.md:36>) y [P15](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/P15_M6_AUTONOMY.md:36>).

**Mejora:** añadir un registro de aceptación por decisión/contrato/hito y sus revisiones; definir qué clientes, fixtures y evidencias deben revisarse tras un cambio incompatible. Para los smoke tests descritos “si posible”, registrar por separado no ejecutado, bloqueado y superado. No convertir falta de entorno en aprobación implícita de una integración real.

**Cierre verificable:** cambiar un contrato de aprobación identifica como afectados cliente ChatyGPT, consumidor Athena y pruebas correspondientes, y no deja sus aceptaciones anteriores vigentes sin revisión.

## Otras mejoras acotadas para P00

Estas precisiones no requieren nuevos componentes ni invalidan las decisiones corregidas:

- **Condiciones vacías:** la decisión actual dice que toda lista vacía es TRUE, también en modo `any`. Es una elección explícita de lenguaje y no necesariamente un error; puede activar una política ALLOW sin condiciones. Confirmar que se desea, separar ausencia accidental de una condición de una política deliberadamente incondicional y añadir un caso de aceptación.
- **Combinación de decisiones:** conservar de forma expresa en v0.3 la precedencia de denegación, aprobación e indeterminación, además de las reglas por campo. Las reglas para `in`, `contains`, tipos incompatibles, políticas deshabilitadas/expiradas y revisiones simultáneas deben quedar en el diccionario y corpus normativo, sin decisiones improvisadas en P02.
- **Propiedad y custodia:** entradas como `ExecutionAdmission = Agora/Broker` describen coordinación, pero no una entidad con dos autoridades intercambiables. Distinguir admisión de worker y admisión de inferencia, y aclarar qué registro produce cada propietario. En Artifact separar propietario, productor y custodio.
- **Previsión frente a confirmación:** P06 mantiene `provisional/confirmed` mientras el MVP descarta reserva futura garantizada. Definir qué se confirma —por ejemplo, admisión al comenzar— para que “confirmed” no prometa una GPU reservada a una hora futura.
- **Requisitos heredados:** el inventario debe indicar qué se conserva de OS-0/OS-1 en límites de contexto, clasificación, autoridad de eventos, guardado de secretos y restricciones de acciones sensibles. La concisión de v0.3 no debería borrar requisitos por omisión.

## Orden recomendado de corrección

1. Unificar precedencia y registrar qué decisiones están propuestas y cuáles se aprueban.
2. Completar las salidas y la puerta de P00, conciliando los tipos nuevos con el catálogo.
3. Corregir las dependencias de presupuesto y consulta de certificación antes del E2E.
4. Especificar garantías de entrega, aplicación de deltas y vínculo aprobación/ejecución mediante ejemplos de fallo.
5. Asignar C15 y sus variantes, y completar el control de versiones e impacto de cambios.
6. Formalizar los documentos y fixtures acordados en P00; solo después evaluar la preparación para P01.

No hace falta otra revisión conceptual completa de la arquitectura. La siguiente mejora útil consiste en cerrar estos puntos delimitados y producir la documentación normativa que el propio paquete ya exige.

## Resultado final

**v0.3 es la versión más consistente de las revisadas y permite reconocer varias correcciones como resueltas en el diseño.** Mantendría `draft-reviewable` hasta ajustar las ocho observaciones y completar la puerta documental, sin equiparar ese trabajo pendiente con falta de implementación.

Se han conservado los archivos recibidos y los informes anteriores. La entrega añadida al proyecto es este informe: no se han modificado decisiones, prompts, contratos ni aplicaciones y no se ha iniciado desarrollo.
