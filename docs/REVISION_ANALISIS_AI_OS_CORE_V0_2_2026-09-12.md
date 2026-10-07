# Revisión de AI OS Core — kit v0.2

Fecha: 12 de septiembre de 2026. Objeto: revisión de `AI_OS_Core_Prompts_v0_2` y contraste con la revisión anterior. No se han ejecutado los prompts ni iniciado desarrollo.

## Dictamen

**La v0.2 mejora sustancialmente el plan de trabajo y corrige varias decisiones de diseño, pero todavía no constituye la especificación contractual corregida y cerrada.** Es una base útil para completar el análisis. Antes de utilizarla como guía de implementación conviene corregir las reglas e inconsistencias señaladas aquí y completar el bloque documental 00A–00F.

La distinción principal es entre **incorporar una corrección al encargo** y **entregar la decisión o documento que la resuelve**. Esta versión hace bien lo primero en muchos puntos. Por ejemplo, pide crear el inventario, definir las transiciones y completar la matriz de autorización, pero esos entregables todavía no están presentes. Esto es normal en un kit de prompts; lo que debe ajustarse es la afirmación del README y del changelog de que los hallazgos ya están corregidos.

No recomiendo rehacer la arquitectura. Sí recomiendo completar la especificación con decisiones concretas y ejemplos de resultado esperado, evitando otra ronda que solo añada instrucciones para decidir más adelante.

| Aspecto | Valoración actual |
|---|---|
| Separación de responsabilidades | Mejor y más precisa, especialmente respecto a Agora |
| Incorporación de la revisión anterior | Amplia; aborda los 19 temas, con distintos grados de cierre |
| Calidad del kit como plan documental | Buena base, pendiente de las correcciones de este informe |
| Inventario y contratos efectivos | Solicitados, todavía no entregados |
| Seguridad, permisos y certificación | Principios más sólidos; algunas reglas siguen ambiguas |
| Recuperación y eventos | Avance importante, con casos límite pendientes |
| Fases y dependencias | Mejor numeración, pero quedan entregables sin asignación suficiente |
| Preparación para desarrollar | Pendiente; el propio prompt 01 exige aprobar 00A–00F |

## Alcance y comprobaciones

Se han leído los **28 archivos de la v0.2**: 21 prompts y siete archivos de apoyo. Se han contrastado con los 19 hallazgos y las incoherencias puntuales de la [revisión anterior](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_ANALISIS_AI_OS_CORE_2026-09-12.md>), así como con los originales OS-0/OS-1.

Comprobaciones realizadas:

- `manifest.json` es válido; sus 21 entradas existen y no se repiten. El orden coincide exactamente con el README.
- No se han encontrado `CONTRACT_INVENTORY.md`, `DATA_DICTIONARY.md`, esquemas ni fixtures de contratos en `AI_OS_core/docs`. Los manifiestos de los kits no son esquemas de los contratos de la aplicación.
- Los 20 archivos analizados en la primera revisión conservan sus hashes: OS-0, OS-1 y el kit v0.1 no han sido modificados desde aquella revisión.
- El Markdown nuevo no presenta los encabezados escapados de OS-0. El original OS-0 conserva sus 158 encabezados escapados y 795 secuencias literales `&#x20;`. Por tanto, la limpieza está encargada en 00A, pero no realizada sobre el original.
- Se han vuelto a inspeccionar las fuentes relevantes de Agora, Model Drift, Athena y KO. Las correcciones propuestas respecto a sus identidades, huellas y consultas siguen concordando con lo observado.
- Se ha consultado documentación oficial de SQLite y realizado una comprobación aislada en memoria de una regla de configuración. No se ha creado ni modificado una base de datos de producto; esa comprobación no acredita comportamiento ante un corte eléctrico.

El contraste con las aplicaciones es estático y selectivo. No acredita integración real, seguridad en ejecución ni rendimiento. La localización del servidor Broker continúa expresamente pendiente en el propio kit; no se ha sustituido esa incertidumbre por una suposición.

## Mejoras que sí están incorporadas

1. **Estado honesto de borrador y hoja de ruta más clara.** Se separan OS-8 Policy, OS-9 Planner y OS-10 Autonomía; el contrato deja de darse por congelado. La certificación manual del prompt 03 y su automatización en el 11 ya se distinguen.
2. **Identidades compatibles con los sistemas actuales.** El [prompt 05](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/05_AGORA.md:9>) conserva la identidad nativa de Agora y reconoce `extra=forbid`. Esto coincide con el [contrato actual](<D:/Desarrollo/Proyectos TFM/Agora/src/agora/api/contracts.py:10>).
3. **Evidencia de modelo y certificación mejor separadas.** El [prompt 03](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/03_AI_BROKER_MODEL_DRIFT.md:48>) mantiene capas, procedencia y comparabilidad parcial, coherentemente con [Model Drift](<D:/Desarrollo/Proyectos TFM/Model_Drift/model_drift/fingerprint.py:32>). Un hash ya no se presenta como prueba suficiente de identidad.
4. **Control del modelo efectivo.** El [prompt 04](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/04_ATHENA.md:17>) distingue modelo solicitado, servido y fallback, y exige rechazar antes de ejecutar si no puede imponerse la restricción. Queda por distribuir completamente su implementación entre fases.
5. **Contexto reproducible y privacidad de exclusiones.** Se exige contenido recuperable o materializado y se distingue conservación histórica de vigencia para usos nuevos. El [prompt 07](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/07_KNOWLEDGE_ORCHESTRATOR.md:9>) también reconoce correctamente la consulta durable de KO, visible en sus [rutas actuales](<D:/Desarrollo/Proyectos TFM/Knowledge_Orchestrator/src/knowledge_orchestrator/api/openapi.py:77>).
6. **Mejoras concretas de recuperación.** El [prompt 00D](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00D_EVENTOS_IDEMPOTENCIA_DURABILIDAD.md:39>) exige no retroceder revisiones y hacer atómicos los efectos locales con su registro de procesamiento.
7. **Planificación mejor representada.** Se añaden intervalos humanos, incertidumbre cuando falta historial y distinción entre capacidad observada y reserva. El mapa incorpora Agora Board/API y las integraciones opcionales ya no bloquean el recorrido principal.

Estas mejoras son reales en el texto. No deben confundirse con contratos terminados o pruebas superadas.

## Seguimiento de los 19 hallazgos anteriores

“Principio corregido” significa que la regla rectora ya se expresa adecuadamente. “Parcial” significa que quedan decisiones necesarias. “Encargado” significa que el kit solicita el entregable, sin que se haya encontrado su resultado. Ninguna etiqueta acredita software implementado.

| Hallazgo anterior | Estado en v0.2 | Evidencia y trabajo restante |
|---|---|---|
| H01. Formato de OS-0 | Encargado | 00A pide normalizarlo; el archivo original sigue igual |
| H02. Inventario de contratos | Parcial | 00A amplía la lista; falta el inventario final y hay nombres nuevos sin conciliar |
| H03. Semántica de políticas | Parcial | 00C mejora UNKNOWN y acumulación; falta lógica completa y corregir el AND genérico del 13 |
| H04. Aprobación exacta | Parcial | 00C añade digest, identidad y revisión; falta separar grant inmutable y consumo, y cerrar alcance/revocación |
| H05. Huellas y aplicabilidad | Principio corregido | 03 conserva evidencia y separa veredicto/aplicabilidad; faltan contratos y reglas concretas de comparación |
| H06. Modelo servido certificado | Parcial | 04 y 11 exigen enforcement; no queda completo su prerrequisito en Broker antes del E2E |
| H07. Contexto reproducible | Principio corregido | 07/12 exigen revisión o snapshot recuperable; custodia y plazos siguen por decidir |
| H08. Atomicidad e idempotencia | Parcial | 00D fija transacciones locales; recuperación de operaciones en curso y resultado idempotente requieren detalle |
| H09. Entrega y orden | Parcial | 00D incorpora replay/revisiones; falta semántica de reinicios y del payload que se compara |
| H10. Durabilidad SQLite | Parcial | Se corrige NORMAL frente a corte eléctrico; aparece una elección “por tabla” que debe reformularse |
| H11. Identidades actuales/globales | Principio corregido | 00E/05 evitan migrar IDs nativos; binding y revisión efectiva aún deben especificarse |
| H12. Transiciones y agregación | Encargado | 00E pide tablas y enumera estrategias; no incluye las tablas ni sus resultados |
| H13. Planificación híbrida/reservas | Parcial | 06 incorpora intervalos; no está decidido quién admite/reserva ni cómo se consume la reserva |
| H14. URLs de servicios | Principio corregido | 00F añade allowlist por identidad, redirecciones, límites y autenticación de enlaces |
| H15. Autorización y clasificación | Parcial | 00C separa petición y permiso, protege exclusiones; la matriz efectiva aún no existe |
| H16. Fases y prompts | Parcial | Roadmap y certificación manual/automática mejorados; quedan dependencias y entregables sin dueño claro |
| H17. Mapa físico/repositorios | Parcial | REPO_MAP corrige nombres y sitúa Board/API; Broker y emplazamiento concreto de Model Drift siguen abiertos, de forma reconocida |
| H18. Persistencia sin pérdida | Encargado | 00E pide la matriz, pero todavía no se entrega |
| H19. Producto/MVP | Parcial | 00F identifica tres recorridos; falta separar demostración aislada y E2E, y acordar objetivos medibles |

Las incoherencias puntuales anteriores también tienen distinto estado: `job.blocked` y el alcance de la autoridad de Agora se corrigen explícitamente; health y custodia de Artifact se separan como conceptos; otras correcciones se delegan a 00B. La consulta histórica de certificación por ID y el mapeo de actores no quedan resueltos expresamente en la v0.2. La precedencia frente a los documentos antiguos importa para no perder esos requisitos.

## Hallazgos de esta revisión

Las prioridades se refieren al documento: **alta**, corregir antes de convertir el kit en encargo de implementación; **media**, cerrar antes de comenzar la fase afectada. No son vulnerabilidades comprobadas en un servicio existente.

### R01 — Alta: el changelog presenta encargos como correcciones ya entregadas

**Evidencia:** el [README, línea 4](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/README.md:4>) afirma que corrige los hallazgos. El [changelog](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/CHANGELOG_v0_2.md:8>) dice que se añade un inventario y máquinas de estados, pero [00A](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00A_NORMALIZACION_E_INVENTARIO.md:22>) y [00E](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00E_IDENTIDADES_ESTADOS_Y_PERSISTENCIA.md:28>) solo ordenan crearlos. No se han encontrado esos resultados.

La v0.2 sustituye explícitamente al kit v0.1, pero no define con suficiente precisión la autoridad y precedencia de OS-0/OS-1, que conservan reglas y versiones anteriores. Por ejemplo, el nuevo cliente consume contratos 0.2 mientras los ejemplos maestros siguen declarando 1.0.

**Mejora:** cambiar esas afirmaciones por “incorpora instrucciones para resolver…” donde corresponda y añadir estado/evidencia de cada corrección. Designar una fuente normativa por contrato y cómo se actualizan o se archivan los documentos antiguos. No se exige implementar el servicio ni ejecutar todos los prompts para reconocer que el kit ha mejorado; sí evitar que un lector crea que las decisiones ya están cerradas.

### R02 — Alta: AND no sirve como combinación universal de requisitos booleanos

**Evidencia:** el [prompt 13](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/13_POLICY_ENGINE.md:22>) prescribe `boolean requirement => AND`.

Si un campo significa `requires_approval`, una política con `true` y otra con `false` producirían `false` mediante AND: se perdería la aprobación exigida. Si significa `allowed`, AND puede ser correcto. Si se trata de conjunción de predicados completos, también puede ser correcto, pero eso es otra representación.

**Mejora:** definir por campo su significado, valor neutro y combinación. Para obligaciones positivas, cualquier obligación activa se conserva; para permisos, se requiere la intersección de lo permitido. Añadir resultados para ausente, `null` y UNKNOWN. Una tabla de verdad de cuatro o cinco ejemplos resolvería esta ambigüedad mejor que la regla genérica actual.

### R03 — Alta: el perfil de durabilidad de SQLite no es una propiedad por tabla

**Evidencia:** [00D, líneas 67–74](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00D_EVENTOS_IDEMPOTENCIA_DURABILIDAD.md:67>) corrige la garantía de NORMAL, pero pide elegir perfil “por tabla/operación”.

`synchronous` se configura para la base/esquema en una conexión, no como atributo independiente de una tabla. Una transacción que modifica Goal, evento e idempotencia no puede aplicar FULL a una tabla y NORMAL a otra de esa misma base. La documentación oficial muestra `PRAGMA schema.synchronous`; la comprobación local también confirmó que cambiar el nivel dentro de una transacción activa se rechaza. [SQLite PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous).

**Mejora:** elegir un perfil para el almacenamiento transaccional del Core, o especificar cuidadosamente una política de conexiones/transacciones completa antes de abrirlas. No separar datos relacionados en varias bases WAL solo para asignar perfiles: SQLite no garantiza atomicidad conjunta de transacciones entre bases adjuntas en WAL. [SQLite WAL](https://www.sqlite.org/wal.html).

La corrección anterior sobre NORMAL sigue siendo válida; este hallazgo afecta a cómo se concreta ahora. No hace falta simular cortes eléctricos en esta revisión documental.

### R04 — Alta: ApprovalGrant necesita separar concesión, consumo y revocación

**Evidencia:** [00C, líneas 58–64](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00C_POLICIES_APPROVALS_AUTH.md:58>) exige que el grant sea inmutable y que registre `consumed_at` y se invalide ante cambios. No especifica si esos datos posteriores son parte mutable del grant, una proyección o eventos separados.

Tampoco queda completamente resuelta la relación entre digest exacto y aprobación por alcance. Una autorización de alcance puede cubrir acciones distintas; un grant ligado a un digest exacto solo cubre la acción que ese digest representa, salvo que se defina una derivación explícita.

**Mejora:** mantener inmutables los términos aprobados y modelar aparte consumo, revocación y validez efectiva. Distinguir una autorización de alcance y las autorizaciones concretas derivadas de ella, o limitar expresamente el alcance a repeticiones de la misma acción. Definir consumo atómico, `max_uses`, revocación manual y tratamiento del reintento después de una respuesta perdida. Vencer o revocar el permiso debe impedir acciones nuevas, sin convertir un reintento de la operación ya aceptada en una acción adicional.

### R05 — Alta: el E2E exige funciones sin una fase de entrega suficientemente asignada

**Evidencia:** el [prompt 10](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/10_E2E_SIN_AUTONOMIA.md:6>) depende de “01–08 relevantes” e incluye aprobaciones, reserva, creación de Job y restricción de modelo efectivo. La cobertura anterior queda incompleta:

| Función requerida | Qué falta asignar de forma explícita |
|---|---|
| Servidor de aprobaciones consumido por ChatyGPT | [01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/01_CORE_MVP_FUNDACION.md:27>) deja almacenamiento mínimo condicional; 02 no entrega operaciones de aprobación/consumo; [08](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/08_CHATYGPT.md:13>) ya necesita validación del servidor |
| Puente Task→Job y agregación de sus estados | [06](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/06_GESTION_TAREAS_IA.md:43>) desarrolla reservas y pruebas, pero no asigna claramente la creación idempotente del Job y el consumo de su ciclo de vida |
| Admisión/reserva efectiva | 06 deja el propietario entre Broker/Runner/Resource Manager; la matriz no asigna su entrega a una fase/proyecto concreto |
| Restricción de candidatos en Broker antes de inferir | [03](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/03_AI_BROKER_MODEL_DRIFT.md:15>) entrega identidad/capacidad/certificación manual; [04](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/04_ATHENA.md:25>) exige soporte del proveedor; [11](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/11_CERTIFICACION_AUTOMATIZADA.md:33>) vuelve a asignar el gate después del E2E |

No afirmo que ninguna de esas capacidades exista en las aplicaciones: el problema es que el kit no demuestra su cobertura ni asigna completamente el trabajo pendiente.

**Mejora:** añadir una matriz requisito E2E → contrato → propietario → prompt que lo entrega → evidencia. Adelantar el gate necesario a la integración base o acreditar que ya existe; reservar 11 para automatización. La fase 10 debería verificar integraciones entregadas, no descubrir e implementar implícitamente servicios nuevos.

### R06 — Alta: “misma revisión y payload distinto” puede rechazar eventos legítimos

**Evidencia:** [00D, línea 43](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00D_EVENTOS_IDEMPOTENCIA_DURABILIDAD.md:43>) y [02, línea 36](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/02_CORE_REGISTRY_EVENTS_POLICIES.md:32>) convierten esa condición en conflicto/cuarentena.

Una revisión puede producir un evento de estado y otro de auditoría con payloads diferentes. También una reconciliación puede devolver un snapshot completo mientras un evento contiene solo el cambio. Comparar literalmente esos payloads no demuestra inconsistencia de estado.

**Mejora:** separar tres controles: mismo `event_id` con contenido incompatible; misma revisión con representaciones contradictorias del mismo estado canónico; y eventos distintos asociados legítimamente a la misma revisión. Precisar si los eventos transportan snapshot o delta y sobre qué contenido se calcula el digest. Si se desea prohibir varios eventos por revisión, hacerlo explícito y compatible con auditoría y notificaciones.

### R07 — Media: los contratos nuevos todavía tienen nombres y ubicaciones inconsistentes

**Evidencia:** el inventario mínimo de [00A](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00A_NORMALIZACION_E_INVENTARIO.md:28>) no incluye algunos tipos que otros prompts introducen, ni aclara estos pares:

| Nombre en un lugar | Nombre o uso posterior | Decisión pendiente |
|---|---|---|
| `HumanInterval` | `HumanIntervalRequirement` en 06 | Intervalo asignado frente a requisito, o un único tipo con nombre canónico |
| `ComparabilityResult` | `ComparabilityAssessment` en 11 | Mensaje, resultado o nombre del proceso; no asumir equivalencia |
| Inventario inicial | `IdentityBinding` en 00E, `EvaluationVerdict` en 03, `TypedPlanProposal` en 14 | Incorporarlos o clasificarlos expresamente como tipos internos/reservados |
| `AIReservation/AdmissionResult` | Dos alternativas de integración en 06 | Definir si ambos existen y cómo se relacionan |

Que 00A diga “como mínimo” permite ampliar la lista; no es un error por sí solo. La incoherencia sería declarar el inventario completo sin conciliar estos nombres.

**Mejora:** un nombre canónico por concepto, con referencia a su definición y fase. El inventario debe revisarse también después de 00C–00F y reservar de forma explícita los tipos futuros. No convertir automáticamente todos esos nombres en entidades persistidas o servicios nuevos.

### R08 — Media: sigue sin cerrarse la semántica determinista completa

**Evidencia:** [00C](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00C_POLICIES_APPROVALS_AUTH.md:14>) pide definir ausentes/null y el default por operación, y permite “DENY/INDETERMINATE según causa”, sin enumerar todavía esas causas.

Persisten preguntas como: ¿las condiciones se combinan con all/any?, ¿qué da una lista vacía?, ¿cómo se combinan FALSE y UNKNOWN?, ¿qué ocurre con operadores no soportados?, ¿qué políticas se aplican cuando varias revisiones coexisten? Enumerar TRUE/FALSE/UNKNOWN no resuelve por sí solo esas decisiones.

**Mejora:** incluir tablas normativas de operadores y composición, defaults por operación y ejemplos de entrada/salida. Añadir un caso de presupuesto con gasto ya reservado para evitar que dos decisiones concurrentes autoricen cada una el total disponible. La evaluación de límites y su cumplimiento en el ejecutor deben tener responsabilidades claras.

### R09 — Media: replay y recuperación necesitan una identidad temporal y un horizonte definidos

**Evidencia:** [00D](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00D_EVENTOS_IDEMPOTENCIA_DURABILIDAD.md:14>) admite secuencia “por productor o stream”; 05 usa revisión nativa “si existe”; los [casos críticos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/CASOS_ACEPTACION_CRITICOS.md:19>) exigen restaurar y reproducir sin duplicar efectos.

Falta decidir qué identifica el stream, cómo cambia tras reinstalación/restauración, qué revisión crea un adaptador cuando el propietario no tiene una, qué ocurre al superar la retención del productor y cómo se recuperan operaciones `in_progress`. Restaurar una copia antigua puede perder el registro de idempotencia de una acción externa ya realizada; repetir outboxes no garantiza por sí mismo ausencia de duplicados.

**Mejora:** definir identidad de productor/stream y época, asignación durable de secuencias, horizonte de deduplicación y una salida explícita para gaps no recuperables. Acordar cómo reconciliar efectos externos después de restaurar, sin volver a ejecutarlos a ciegas. Documentar la unidad atómica entre efecto de negocio y resultado idempotente. Mantener estas garantías separadas de la caída ordinaria del proceso.

### R10 — Media: el README promete una estructura de prompts y puertas que no se cumple aún

**Evidencia:** el [README](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/README.md:44>) afirma que cada prompt declara prerrequisitos, repositorios, entregables exclusivos, pruebas con fixtures, pruebas reales y evidencia de cierre. Solo 10 de los 21 prompts incluyen una sección explícita de prerrequisitos; varios tampoco distinguen pruebas documentales y reales. El orden lineal ayuda, pero no resuelve dependencias funcionales como las de R05.

[00B](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00B_CONTRATOS_MAESTROS.md:40>) produce esquemas/fixtures antes de que 00C–00E completen semántica, estados y persistencia. Es un orden viable por refinamiento, siempre que obligue a revisar los artefactos afectados y a invalidar su aceptación anterior. Además, el bloque “previo a código” permite esquemas Pydantic: debe distinguir formalización de contratos y código de producto para no inducir a ejecutar trabajo fuera de alcance.

**Mejora:** describir para cada prompt entradas versionadas, salidas, responsable y evidencia de aceptación, con “no aplica” cuando corresponda. Separar puerta documental, pruebas aisladas y pruebas reales; registrar una revisión concreta aceptada. Reabrir decisiones afectadas por cambios posteriores. Los casos críticos necesitan resultado esperado y condición de cierre, no solo el nombre del escenario. Mantener la integración opcional 09 fuera de los prerrequisitos obligatorios.

### R11 — Media: el mínimo de autonomía mezcla magnitudes no comparables

**Evidencia:** el [prompt 15](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/15_AUTONOMIA_CONDICIONAL.md:14>) define el nivel efectivo como mínimo entre techo de capability, política, certificación/aplicabilidad, scope y restricciones de riesgo/recursos.

Los niveles A0–A5 son ordenables; `stale`, `not_applicable`, un scope o una reserva de GPU no son niveles de autonomía. No existe un mínimo entre esos tipos sin una transformación explícita. Tampoco conviene que el resultado simplemente A0 oculte la diferencia entre “solo observar” y “acción bloqueada por falta de autorización”.

**Mejora:** obtener primero las decisiones de autorización, certificación y admisión; cualquier bloqueo necesario debe conservar su motivo. Calcular después el mínimo solo entre techos expresados en A0–A5 y mantener las obligaciones de aprobación y coste por separado. No es preciso diseñar toda OS-10 ahora, pero sí evitar una fórmula que parece ejecutable y aún no lo es.

### R12 — Media: faltan límites claros entre el MVP aislado, el integrado y el Planner futuro

**Evidencia:** [00F](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/00F_PLAN_FISICO_REPOS_Y_MVP.md:37>) incluye trazabilidad de un flujo manual Task→Job→Run→Artifact entre los tres recorridos del primer Core, pero el E2E real llega en 10. El [prompt 14](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_2/14_PLANNER_TIPADO.md:9>) añade inferencia vía Broker y la matriz menciona Core/Broker/Tasks, sin precisar dónde reside el Planner ni reconciliarlo expresamente con las restricciones del Core en OS-0.

**Mejora:** diferenciar aceptación del Core con eventos de ejemplo y demostración integrada con productores reales. Documentar qué parte entrega cada hito. Para el Planner, declarar quién solicita inferencia, quién posee la propuesta y quién confirma/crea tareas, y actualizar la decisión maestra si cambia su frontera. Preservar explícitamente los límites de contexto y costes heredados, indicando qué sigue vigente y qué se sustituye. La v0.2 debe permitir leer el alcance sin reconstruirlo entre versiones.

## Ajustes recomendados, en orden

1. **Corregir el kit antes de ampliarlo:** R02 (booleanos), R03 (SQLite), R04 (grant y ciclo de vida) y R06 (comparación de revisiones/payloads).
2. **Ajustar las afirmaciones de estado y la fuente normativa:** distinguir cambios ya incorporados, decisiones por cerrar y entregables no creados. Establecer la precedencia entre v0.2, OS-0 y OS-1.
3. **Completar la matriz de dependencias y responsabilidades:** aprobaciones, Task→Job, reservas y gate del Broker deben tener propietario y entrega previa al E2E.
4. **Materializar el cierre documental:** inventario, diccionario, transiciones, matriz de autorización, reglas de políticas y decisiones de recuperación. Puede hacerse como documentación y tablas; esta revisión no autoriza su implementación.
5. **Resolver los casos con resultados esperados:** en particular, dos políticas que discrepan sobre una obligación, dos eventos legítimos de una revisión, aprobación de alcance y restauración con efectos externos ya realizados.
6. **Registrar aprobación por versión de documento:** una casilla o un manifest válido no sustituyen la evidencia de que un contrato concreto está completo y es coherente con sus consumidores.

No es necesario añadir más servicios, un motor de reglas más complejo o una base de grafos para corregir estos puntos. La mejora inmediata consiste en reducir ambigüedad y asignar responsabilidades verificables.

## Resultado de la revisión

La v0.2 es **mejor que la v0.1 como guía de trabajo** y recoge correctamente buena parte de la crítica anterior. Las correcciones sobre propiedad, modelo efectivo, comparabilidad y evidencia reproducible merecen conservarse.

La conclusión de cierre sigue siendo **pendiente de especificación**, con una razón más precisa que antes: ya existe un itinerario documental para resolverla, pero faltan sus resultados y algunas reglas nuevas necesitan ajuste. Recomiendo mantener `draft-reviewable` y completar el análisis antes de habilitar el prompt 01.

Se han conservado todos los archivos recibidos y el informe anterior. La entrega añadida al proyecto es este informe; no se han cambiado prompts, contratos, aplicaciones ni integraciones.
