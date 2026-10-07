# Revisión del análisis de AI OS Core

Fecha: 12 de septiembre de 2026. Alcance: revisión documental y contraste selectivo con código y documentación existentes. No se ha iniciado el desarrollo ni se han modificado los documentos analizados.

## Dictamen

**La propuesta es coherente como arquitectura de intención, pero todavía no está cerrada como contrato de integración ni suficientemente definida para ejecutar sus prompts de implementación sin tomar decisiones nuevas.** Recomiendo mantener OS-0 y OS-1 en estado de borrador revisable y corregir primero las cuestiones de prioridad alta de este informe.

El problema no es la elección de un servicio central pequeño. La separación entre objetivos, tareas, ejecución, inferencia y conocimiento tiene sentido y varias premisas están respaldadas por las aplicaciones existentes. El problema es la distancia entre los principios en prosa y las reglas necesarias para que distintos componentes interpreten igual identidades, estados, permisos, eventos y certificaciones.

La frase inicial «He cerrado OS-0» no queda respaldada por el propio criterio de cierre del documento: todavía hay respuestas que dependerían de decidirlas al programar. El encabezado «propuesta normativa previa a implementación» es más fiel a su estado real. Véanse [inicio de OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:1>) y [criterio de cierre](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:6765>).

| Dimensión | Estado de la documentación |
|---|---|
| Propósito y separación de responsabilidades | Bien orientados; conviene conservarlos |
| Correspondencia con aplicaciones existentes | Parcialmente contrastada; requiere contratos de adaptación explícitos |
| Contratos de datos y API | Incompletos y con discrepancias concretas |
| Eventos, recuperación e idempotencia | Buenos principios; garantías operativas pendientes |
| Certificación, políticas y aprobaciones | Diseño prometedor, todavía ambiguo en decisiones críticas |
| Contexto y privacidad | Reglas acertadas, sin mecanismo suficiente de reproducción y autorización |
| Planificación humana e IA | Distinción correcta; modelo temporal y de reserva incompleto |
| Fases y prompts | Útiles como orientación; necesitan sincronización y prerrequisitos |
| Preparación para desarrollo | No recomendaría congelar aún la versión contractual 1.0 |

Esta valoración no es un porcentaje de avance de software. En `AI_OS_core` se ha encontrado únicamente la carpeta de documentación: la ausencia de implementación es coherente con la fase actual y no se cuenta como defecto.

## Material y método

Se han leído los **20 archivos originales** de `docs`: OS-0, OS-1 y los 18 archivos del kit, que contienen 14 prompts, README, checklist, matriz de repositorios y manifest. Se han comprobado su consistencia interna, referencias cruzadas, ejemplos y correspondencia selectiva con las aplicaciones que invocan.

Documentos principales: [OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md>), [OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md>) y [kit de prompts](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/README.md>).

El índice Graphify existente no contiene referencias a AI_OS_core. Se han utilizado los originales como evidencia. El conector codebase-memory-mcp no estaba disponible en esta sesión. El contraste de aplicaciones es una inspección estática acotada, no una auditoría exhaustiva de sus implementaciones ni una prueba de integración en funcionamiento.

Las afirmaciones técnicas externas sobre SQLite y seguridad se han contrastado con documentación primaria, enlazada donde se usa. Las observaciones se clasifican como **error comprobado**, **vacío de especificación** o **mejora recomendada**. Prioridad alta significa resolver antes de congelar el contrato correspondiente; prioridad media significa resolver antes de iniciar la fase que lo consume. No implica que exista una vulnerabilidad demostrada en una aplicación ejecutándose.

## Lo que está bien y conviene mantener

- Un propietario por dominio y referencias federadas, con reconciliación a favor de la fuente autorizada. Evita convertir el Core en una segunda base de datos de cada aplicación.
- Separar Goal, Objective, Task, Job y Agent Run; distinguir hechos de órdenes; no convertir al LLM en autoridad sobre políticas o permisos.
- Mantener el Core operativo sin GPU ni servicios externos, con integración aditiva y funcionamiento independiente de las aplicaciones.
- Diferenciar tiempo humano activo y cómputo IA; conservar Google Calendar como fuente externa de solo lectura.
- Proyectar certificaciones de Model Drift y conservar ejecución y verificación en los componentes especializados.
- SQLite local, transacciones cortas y copias mediante su API de backup son elecciones defendibles para una primera versión de alcance acotado. WAL permite concurrencia entre lectores y escritor, pero mantiene un único escritor simultáneo; esto concuerda con OS-1. La API de backup es una elección adecuada para una base abierta. Fuentes: [SQLite WAL](https://www.sqlite.org/wal.html) y [SQLite Backup API](https://www.sqlite.org/backup.html).

## Contraste con las aplicaciones existentes

| Premisa del análisis | Evidencia consultada | Resultado y límite |
|---|---|---|
| Gestión de Tareas mantiene Calendar en solo lectura | [Scope OAuth en código](<D:/Desarrollo/Proyectos TFM/Gestion Tareas IA/src/pomodoro_planner/integrations/google_calendar.py:16>) y [estado documentado](<D:/Desarrollo/Proyectos TFM/Gestion Tareas IA/docs/CURRENT_STATE.md:14>) | Respaldada. La planificación humana/IA propuesta sigue siendo una ampliación, no una capacidad acreditada por este contraste |
| Athena tiene permisos, verificación y recuperación | [Estado del runtime](<D:/Desarrollo/Proyectos TFM/Athena/docs/CURRENT_STATE.md:9>) y [reglas de skills](<D:/Desarrollo/Proyectos TFM/Athena/src/athena/skills.py:1>) | Respaldada en documentación y diseño del código; no se han ejecutado sus flujos |
| Agora tiene Board durable y reclamación atómica | [README](<D:/Desarrollo/Proyectos TFM/Agora/README.md:3>) y [Board.claim](<D:/Desarrollo/Proyectos TFM/Agora/src/agora/board.py:96>) | Respaldada estáticamente. Su identidad y contrato actuales no son el Job ULID propuesto |
| Model Drift tiene huellas y políticas de evaluación | [Fingerprint](<D:/Desarrollo/Proyectos TFM/Model_Drift/model_drift/fingerprint.py:1>) y [fundamentos de evaluación](<D:/Desarrollo/Proyectos TFM/Model_Drift/README.md:135>) | Respaldada. La autoridad de certificación interoperable es una ampliación propuesta; su adaptación no debe perder la procedencia ni la comparabilidad parcial |
| KO expone documentos, claims, entidades y consultas | [Definición de rutas](<D:/Desarrollo/Proyectos TFM/Knowledge_Orchestrator/src/knowledge_orchestrator/api/openapi.py:57>) | Respaldada. La consulta IA se describe como durable y tiene consulta posterior de resultado; no se debe presuponer una respuesta síncrona de contenido |
| Local AI Lab tiene puente con Model Drift | [Contrato documentado](<D:/Desarrollo/Proyectos TFM/Local AI Lab/README.md:149>) | Respaldada documentalmente: plan sellado y artefactos, con confirmación humana. No acredita por sí sola publicación de eventos OS-0 |
| Broker ya permite las ampliaciones con cambios mínimos | [Compatibilidad documentada por un consumidor](<D:/Desarrollo/Proyectos TFM/Gestion Tareas IA/docs/CURRENT_STATE.md:30>) | Respaldo indirecto de catálogo/capabilities y negociación. No se ha acreditado aquí el servidor Broker completo ni todas las métricas de hardware, colas y duración propuestas |

Las frases «ya dispone» deberían incluir fecha y enlace a contrato o código. Las expresiones «cambio mínimo» deben tratarse como hipótesis de esfuerzo hasta completar el inventario de diferencias.

## Hallazgos de prioridad alta

### H01. El formato de OS-0 está dañado y sus ejemplos no son directamente reutilizables

**Error comprobado.** Hay 158 encabezados escapados, 795 apariciones literales de `&#x20;` y 432 guiones bajos escapados. Dentro de los bloques de código estas secuencias se conservan literalmente. Al analizar sin transformar los 41 bloques etiquetados `yaml`, **39 fallan en el parser**. Ejemplo: [versionado contractual](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:385>).

Esto no demuestra que todos los conceptos estén mal, ni presupone que los bloques fueran esquemas ejecutables: demuestra que el archivo no puede usarse como fuente literal fiable. Además, incluso tras reparar el formato, mezcla ejemplos, pseudotipos y descripciones de esquema.

**Mejora:** normalizar Markdown e indentación, separar ejemplos de documentos de las definiciones de campos y marcar expresamente el pseudocódigo. La aceptación editorial debería comprobar lectura y copiado correctos, sin transformar silenciosamente los originales en esta revisión.

### H02. El conjunto de contratos a congelar no está completo

**Error comprobado y vacío de especificación.** OS-0 enumera 21 contratos al cierre; el prompt 00 enumera 23 al añadir ApprovalDecision y CommandEnvelope. Ambos dejan fuera de su inventario de cierre contratos usados en el diseño, como CertificationRequest, ServiceRegistration, JobDispatch, CreateJobRequest/Response, VerificationResult, Autonomy y DecisionTrace. Véanse [cierre OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:6207>) y [lista del prompt 00](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/00_OS0_CONTRATOS_Y_REGLAS.md:28>).

No todos tienen que implementarse en OS-1, pero sí debe saberse cuáles son normativos, cuáles son tipos anidados y cuáles quedan reservados para fases futuras. Faltan también obligatoriedad, nulabilidad, formatos de fechas y duraciones, unidades de memoria/utilización, estructura de referencias y reglas de compatibilidad para muchos campos. R0–R4 aparecen sin definición de riesgo. El sobre común se presenta como conceptual y no se aclara cómo se combina con cada entidad.

**Mejora:** crear en la siguiente revisión documental un inventario único con propietario, fase, versión, campos obligatorios, ejemplos, estados y operaciones. No hace falta escribir implementación para cerrar estas decisiones.

### H03. Las políticas no tienen una semántica suficiente para decidir siempre igual

**Vacío de especificación.** La precedencia `DENY > REQUIRE_APPROVAL > CONSTRAIN > ALLOW` y la lista de operadores son un buen inicio, pero no definen cómo combinar condiciones, qué ocurre con un campo ausente o `null`, qué significa una lista vacía, qué resultado se obtiene sin políticas aplicables, ni cómo se acumulan restricciones. Referencias: [políticas OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2103>) y [evaluador OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1422>).

Por ejemplo, elegir REQUIRE_APPROVAL como único efecto ganador podría perder un límite de gasto impuesto por otra política CONSTRAIN. Dos límites de recursos incompatibles tampoco se resuelven simplemente con prioridad. La política de ejemplo que rechaza cualquier estado distinto de `certified` es válida como política estricta particular, pero no debe confundirse con la regla global que admite DEGRADED según política.

**Mejora:** definir la combinación explícita de decisión, obligaciones y límites; resultado para información desconocida; desempates; y tabla de ejemplos. Una aprobación no debe eliminar restricciones vigentes. Para una acción que requiere autorización, la ausencia de datos no debería interpretarse como permiso implícito.

### H04. Falta vincular una aprobación a la acción exacta y a quien puede aprobarla

**Vacío de especificación.** ApprovalRequest y ApprovalDecision recogen estado, vencimiento y decisión, pero no cierran el vínculo con la versión de la acción, su consumo único, revocación, identidad autorizada ni la carrera entre aprobación y expiración. `approve_scope` no tiene límites suficientemente definidos. Véanse [ApprovalRequest/Decision](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5175>) y [API de aprobación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1097>).

Ejemplo: el usuario aprueba una acción con un destino concreto; después cambia el destino o se reintenta la orden como una acción nueva. El diseño debe explicar por qué la aprobación anterior sirve o deja de servir.

**Mejora:** vincular aprobación a identidad autenticada, acción y recursos versionados, alcance, expiración y política aplicable. Diferenciar reutilización legítima de la misma operación y autorización para una nueva. Precisar también la relación con las aprobaciones locales de Athena, que conserva sus permisos: si el Core solo proyecta esas solicitudes o puede transmitir decisiones reconocidas por el runtime. El servidor debe validar transiciones y permisos; la UI no puede ser la única barrera. Referencia técnica: [OWASP REST Security](https://cheatsheetseries.owasp.org/cheatsheets/REST_Security_Cheat_Sheet.html).

### H05. El fingerprint propuesto pierde distinciones que Model Drift ya conserva

**Diferencia comprobada y vacío de adaptación.** OS-0 define valores planos y `null` para lo no verificable; OS-1 persiste `fingerprint_hash`. Model Drift conserva por componente valor, estado declarado/verificado/no disponible y capa de identidad, y advierte expresamente que el hash no basta para comparar. Véanse [fingerprint OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:1333>), [persistencia OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:669>) y [modelo existente](<D:/Desarrollo/Proyectos TFM/Model_Drift/model_drift/fingerprint.py:52>).

Que un proveedor empiece a informar un dato antes desconocido puede cambiar el hash sin acreditar un cambio real del modelo. A la inversa, dos huellas con componentes críticos desconocidos no acreditan identidad completa. El diseño tampoco representa claramente `stale` o `not_applicable`, que usa en el texto pero no incluye en el estado contractual de Certification.

**Mejora:** conservar procedencia y cobertura; separar identidad indexable, comparabilidad, resultado de evaluación y aplicabilidad de una certificación al candidato actual. Mantener la certificación histórica vinculada a su combinación original, sin cambiar su veredicto porque aparezca otra. Definir expiración, frescura y qué hacer cuando falta evidencia crítica. Si se introduce un hash interoperable, especificar campos incluidos y serialización canónica; excluir marcas de observación del identificador estable. [RFC 8785](https://datatracker.ietf.org/doc/html/rfc8785) describe una opción de canonicalización JSON, no una solución a la comparación semántica.

### H06. No está cerrado el control entre modelo certificado y modelo realmente servido

**Vacío de especificación.** Agora comprueba requisitos y el Broker decide modelo/estrategia; OS-0 presenta el routing consciente de certificación como opcional posterior. No se define el protocolo que impide seleccionar o usar como fallback un modelo distinto del autorizado. Referencias: [gate](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5795>), [ampliación Broker](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:6307>) y [prompt Agora](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/05_OS2_AGORA.md:39>).

El problema existe también si el modelo cambia entre la comprobación y la ejecución. Athena ya distingue elección explícita sin fallback y selección delegada al Broker: [comportamiento actual](<D:/Desarrollo/Proyectos TFM/Athena/docs/CURRENT_STATE.md:28>).

**Mejora:** escoger y documentar un mecanismo: perfil de ejecución fijado, conjunto autorizado de candidatos o autorización verificada por el componente que sirve la inferencia. Revalidar en el punto de ejecución y registrar cada modelo efectivo, incluidos fallbacks. Para un requisito obligatorio, Core/Model Drift inaccesible debe tener una respuesta definida que no convierta información obsoleta en permiso. El modo standalone puede conservarse sin omitir un requisito explícito de un trabajo integrado.

### H07. La inmutabilidad del Context Package no asegura reproducir el contexto recibido

**Vacío de especificación con tensión entre requisitos.** El paquete debe demostrar qué recibió el Run aunque cambie el conocimiento, pero las referencias pueden llevar versión nula y resolverse bajo demanda; además, OS-1 limita su retención. Véanse [ResourceReference](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:487>), [snapshot y consulta diferida](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2517>) y [retención](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:867>).

Una lista inmutable de enlaces mutables conserva la lista, pero no necesariamente el contenido consumido. Conservar solo el hash permite verificar un contenido disponible; no permite recuperarlo si desaparece.

**Mejora:** exigir para lo consumido una revisión inmutable recuperable o un snapshot del contenido, con procedencia y hash. Acordar quién conserva los fragmentos recuperados durante el Run, cómo se incorporan a la trazabilidad y durante cuánto tiempo. Separar expiración para uso nuevo y conservación de evidencia histórica. No es necesario copiar todo KO al Core.

### H08. La recuperación de eventos e idempotencia necesita fronteras transaccionales explícitas

**Vacío de especificación.** Persistir antes de procesar y usar handlers idempotentes es correcto. Sin embargo, el esquema no aclara si evento y trabajo pendiente se crean en una misma transacción o se redescubren de forma determinista al arrancar. Tampoco fija la atomicidad entre efecto del handler y marcado como procesado, ni entre escritura de negocio y resultado idempotente. Véanse [event_processing y flujo](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:754>) e [idempotencia](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:886>).

Ejemplos: caída después de guardar un Goal pero antes de registrar su evento; caída después de actualizar una proyección pero antes de marcar el handler; dos solicitudes simultáneas con la misma clave. El texto no permite deducir aún el resultado en todos esos casos.

**Mejora:** definir unidad atómica de cada operación, unicidad de `(event_id, handler)`, ámbito de clave por identidad y operación, solicitudes en curso, reintentos, expiración y respuesta reproducible. Si un handler produce efectos externos en fases futuras, documentar outbox e idempotencia del receptor. No exigir exactamente una ejecución interna; sí efectos de negocio correctos bajo reintento.

### H09. Faltan entrega durable desde productores y orden de actualización de proyecciones

**Vacío de especificación.** El Core conserva eventos que ha recibido, pero eso no garantiza que otro servicio pueda entregarlos después de una desconexión. `occurred_at`, `recorded_at` y ULID tampoco definen por sí solos el orden de versiones de un recurso. La reconciliación a favor del propietario no determina cuál de dos observaciones del mismo propietario es más reciente. Referencias: [Event](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:1763>), [reconciliación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5539>) y [consulta de eventos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:4137>).

Ejemplo: llega `job.completed` y después un `job.started` retrasado; o la reconciliación obtiene una versión vieja mientras entra un evento más nuevo. No debería retroceder el estado.

**Mejora:** acordar confirmación de recepción, cola persistente del productor o mecanismo de replay, cursor estable, versión/secuencia por recurso, política para eventos tardíos, huecos y duplicados incompatibles. Añadir tratamiento de eventos permanentemente fallidos y procedimiento de reproceso. ULID aporta orden temporal aproximado e identidad; no sustituye una regla causal ni una revisión del recurso. [Especificación ULID](https://github.com/ulid/spec).

### H10. La promesa de durabilidad omite el límite de `synchronous=NORMAL`

**Inexactitud técnica comprobada.** OS-1 prescribe WAL con `synchronous=NORMAL` y describe Event Store y auditoría como durables, sin distinguir caída del proceso y caída del sistema o alimentación. [Configuración OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:508>).

SQLite documenta que WAL con NORMAL mantiene consistencia y sobrevive a una caída de la aplicación, pero una transacción confirmada puede perderse tras caída del sistema o corte eléctrico. Esto no invalida SQLite; obliga a precisar la garantía. [SQLite PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous).

**Mejora:** declarar si se acepta perder confirmaciones recientes ante esos fallos. Si no se acepta para aprobaciones, eventos e idempotencia, especificar la configuración de durabilidad correspondiente, como FULL en WAL, y validarla en el entorno futuro. Añadir objetivos de recuperación y prueba de restauración; un backup no elimina automáticamente esta ventana de pérdida.

### H11. Falta el contrato de adaptación entre identidades actuales y globales

**Diferencia comprobada.** OS-0 pide `<namespace>_<ULID>` para todos los objetos interoperables. Agora documenta que la identidad de una tarjeta sigue siendo `filename`; `external_reference` no es única y puede representar varias tarjetas. Sus solicitudes actuales usan `extra="forbid"`, por lo que añadir campos desconocidos directamente no es una ampliación compatible para ese receptor. Véanse [identidad global](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:159>) y [contrato actual de Agora](<D:/Desarrollo/Proyectos TFM/Agora/src/agora/api/contracts.py:10>).

**Mejora:** definir una correspondencia durable entre identidad global, propietario, instancia/Board e identidad nativa. Decidir cómo tratar cambios de nombre, importaciones y reintentos; no renombrar ni migrar datos existentes por inferencia. Negociar versiones y adaptar solicitudes a las capacidades anunciadas. La versión de esquema, revisión de un recurso, versión de capability y versión de servicio deben tener significados separados.

## Hallazgos de prioridad media

### H12. Estados y progreso carecen de reglas de transición y agregación

**Vacío de especificación.** Hay enumeraciones, pero no tablas de transiciones y precondiciones; Agent Run deja `status` sin enumerar. Task admite varios Jobs y el E2E termina actualizando Task y progreso del Goal sin especificar qué significa completarlos. Véanse [Task–Job](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:3355>), [Agent Run](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:3487>) y [E2E](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/10_OS5_INTEGRACION_END_TO_END.md:14>).

**Mejora:** definir transiciones válidas, cancelación y terminación concurrentes, reanudación, intentos y propagación de bloqueos. Determinar cuándo una Task con varios Jobs se completa y quién verifica los criterios de Objective/Goal. Un Job completado no demuestra automáticamente el resultado deseado. Añadir prevención de ciclos y reglas de actualización concurrente, por ejemplo revisión esperada al editar.

### H13. La planificación necesita intervalos humanos y admisión real de recursos IA

**Vacío de especificación.** Separar tiempo humano y de cómputo es correcto; un total de cinco minutos humanos no indica cuándo se necesitan. Puede haber intervención inicial y revisión final separadas por horas. Los snapshots de capacidad son observaciones y no reservan GPU ni impiden competencia con otras aplicaciones. Véanse [calendario](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2939>), [capacidad](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:3023>) y [prompt de tareas](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/06_OS4_GESTION_TAREAS_IA.md:21>).

La regla «solo replanificar humanos si hay dependencia AI→H» debe incluir explícitamente las fases humanas de tareas híbridas y recursos compartidos. P80/P95 son una política inicial posible, no una garantía de plazo. Sumar percentiles de tareas no produce, en general, el mismo percentil del flujo completo.

**Mejora:** modelar intervalos o subtareas humanas, cola frente a servicio, tareas interrumpibles, recursos exclusivos y quién admite/reserva/libera capacidad al ejecutar. Fijar unidades, zona horaria y tratamiento de cambios de hora. Definir mínimo de muestras, calibración y alternativa explícita cuando no haya historial. No asumir que tiempo de pared equivale siempre a humano más cómputo.

### H14. El registro de servicios introduce un riesgo no cubierto por validar Resource URI

**Vacío de especificación de seguridad.** Un servicio anuncia `base_url` y endpoints; el health worker los consulta. Validar el namespace de `knowledge://...` no protege las solicitudes HTTP hechas contra esas URLs. [ServiceRegistration](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:4349>) y [health worker](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1181>).

**Mejora:** permitir solo destinos, puertos y protocolos asociados a cada servicio autorizado, con controles de redirección, tiempos y tamaños. Las direcciones locales/LAN necesarias deben autorizarse expresamente, no prohibirse indiscriminadamente. Evitar reenviar credenciales a otro destino. Esto complementa autenticación y validación de esquema; son controles contra solicitudes a destinos inducidos, descritos por [OWASP SSRF Prevention](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html).

### H15. La clasificación de datos no define por sí sola quién puede leerlos

**Vacío de especificación.** Se distingue autenticación de usuario/servicio, pero falta una matriz de operaciones y recursos autorizados para cada identidad. El ceiling del ContextRequest es una petición del consumidor, no debería ser su autorización. Además, registrar la referencia de un elemento excluido puede revelar su existencia a quien no puede verlo. [ContextRequest](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2345>), [exclusiones](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1374>) y [autenticación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1505>).

**Mejora:** vincular el principal autenticado con los valores de source/owner/requester; aplicar permisos a eventos, recursos, contexto, auditoría y administración. Calcular el techo efectivo con la intersección de petición, identidad, política y destino; definir valores predeterminados cuando falte clasificación. Separar detalles de exclusión visibles al consumidor y a auditoría. Es una concreción pendiente del principio de mínimo privilegio, no evidencia de una fuga actual.

### H16. El plan de fases y la matriz de cambios no coinciden completamente

**Error comprobado y ambigüedad de planificación.** OS-0 separa OS-8 Policy Engine, OS-9 Planner y OS-10 Conditional Autonomy; el último prompt agrupa Policy Engine y autonomía bajo OS-8, manteniendo Planner como futuro. No queda claro si se ha recortado o renumerado la hoja de ruta. [Fases originales](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:6539>) y [prompt 13](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/13_OS8_POLICY_ENGINE_Y_AUTONOMIA.md:1>).

El prompt 03 incorpora suites y resultados de certificación; el 11 vuelve a ampliar esa materia. Puede ser correcto si se distingue certificación manual de automatización, pero debe decirse. La matriz omite AI_OS_Core en fase 11, aunque ese prompt le asigna crear solicitudes y actualizar disponibilidad. Los prompts 01 y 02 se solapan en Registry, Policies y Context. El README afirma que cada prompt es autosuficiente, aunque dependen de contratos anteriores sin instrucciones precisas de localización y versión.

**Mejora:** distinguir número de prompt y fase arquitectónica; crear una tabla de dependencias, entradas y entregables exclusivos. Indicar qué pruebas usan fixtures y cuáles requieren servicios reales. Actualizar la [matriz](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/MATRIZ_CAMBIOS_REPOS.md:5>). Conservar como opcionales las integraciones de laboratorio y captura para que no bloqueen la ruta principal.

### H17. El mapa físico y los nombres de repositorios requieren precisión

**Omisión comprobada.** El diagrama de despliegue coloca Agora Runner en PC IA, pero omite Agora Board/API en el PC principal y no sitúa Model Drift. Son piezas necesarias para interpretar la ruta de trabajo y certificación. [Diagrama OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:2372>) y [distribución de Agora](<D:/Desarrollo/Proyectos TFM/Agora/README.md:11>).

Los nombres del kit tampoco corresponden literalmente a varias carpetas: `Agora_AGR` frente a `Agora`, `Gestion-tareas-IA` frente a `Gestion Tareas IA` y `Local-AI-Lab` frente a `Local AI Lab`. La carpeta `Broker AI` examinada contiene material de integración, no acredita por sí sola ser el servidor denominado `AI_Broker`.

**Mejora:** añadir un mapa de nombre lógico, ruta real, proceso, máquina, autoridad y contrato público. Precisar si el puente de eventos es relay o productor, y cómo mantiene identidad autenticada del origen. Evitar que un prompt cree un repositorio duplicado por una diferencia de nombre.

### H18. La persistencia no demuestra todavía que conserve todos los contratos

**Vacío de especificación.** Las tablas se describen como campos esenciales, por lo que no es un error no listar cada columna. Aun así, no se explica dónde persisten `success_criteria`, restricciones, proyectos y política de autonomía de Goal; dependencias de Objective; ni todos los atributos del manifiesto de Capability. [Goal contractual](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:599>) y [tablas](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:564>).

Tampoco queda cerrado cómo cargar/versionar Policies y cómo registrar Skills/Certifications: hay referencias a identidad de servicio o consumo de eventos, pero falta elegir el mecanismo y sus payloads. Las consultas de listas necesitan paginación, filtros y orden estables. No hace falta abrir una ruta pública de escritura para cada entidad; sí describir su ciclo de entrada, persistencia y consulta.

**Mejora:** añadir una matriz campo contractual → persistencia/proyección → productor → lectura, y ejemplos de guardar/recuperar sin pérdida. Especificar restricciones de unicidad y relaciones, versiones de proveedor y límites de consultas.

### H19. Falta demostrar el valor del primer producto y acotar su tamaño

**Mejora recomendada.** El análisis justifica la arquitectura, pero no identifica con suficiente precisión el primer problema de usuario, frecuencia de uso, alternativas, coste de mantener otro servicio ni criterios medibles de éxito. OS-1 propone numerosos módulos, tablas, workers e interfaces mientras lo califica repetidamente de pequeño. Eso no prueba sobrediseño, pero tampoco acredita simplicidad.

**Mejora:** añadir una página de alcance: primer usuario, tres recorridos prioritarios, entradas disponibles y resultados observables; distinguir imprescindibles, diferidos y opcionales. Proponer objetivos de latencia, volumen, frescura y recuperación como metas a acordar, no como medidas existentes. Una primera entrega podría centrarse en servicios/capabilities, Goals/Decisions y trazabilidad; la selección final debe reflejar la necesidad real del usuario. La demostración E2E puede planificarse como comprobación manual antes de automatizar decisiones.

## Incoherencias puntuales que conviene corregir

| Punto | Evidencia | Corrección documental propuesta |
|---|---|---|
| El grafo de ejemplo usa `PROVIDED_BY`, fuera de las relaciones permitidas | [Relaciones](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5409>) y [ejemplo](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5477>) | Usar `PROVIDES` con dirección invertida o incorporar formalmente la inversa. Definir también cómo representar Model Fingerprint, que no aparece entre tipos iniciales |
| `job.blocked` aparece como evento de retorno, pero falta en el catálogo mínimo de Agora y en su prompt | [Retorno de estados](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:4827>) y [prompt 05](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_1/05_OS2_AGORA.md:28>) | Unificar catálogo, autoridad y payload. Revisar también `task.failed`, `runtime.changed` y cambios de tools/policy usados por flujos posteriores |
| Health usa vocabularios diferentes | [Health OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:3961>), [estados generales](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:5715>) y [registry OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1147>) | Diferenciar salud propia, observación de conectividad y ciclo del registro, con mapeo explícito. No son necesariamente un único enum |
| `classification_ceiling` es obligatorio en el texto pero falta en ContextPackage; Capability tampoco declara `max_classification` | [Package](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2431>) y [privacidad](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:4471>) | Añadir campos o especificar dónde se derivan, con un vocabulario canónico y permisos asociados |
| Certificación por ID desaparece de la lista de endpoints OS-1 | [OS-0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:4103>) y [OS-1](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:1022>) | Conservar `/{id}` o registrar su aplazamiento; `current` no sustituye la consulta de evidencia histórica |
| Se prohíben workers al describir desviaciones, pero el diseño incluye tres workers internos | [Workers internos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:471>) y [tamaño esperado](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-1 Diseño Interno del Servicio v0.1.md:2346>) | Escribir «workers de ejecución de trabajos de usuario»; mantener separados procesadores internos de eventos, health y reconciliación |
| Artifact carece de propietario único explícito en la tabla inicial | [Ownership](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:85>) y [Artifact](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:3577>) | Definir por artefacto autoridad, custodia, publicación y retención; el productor no tiene por qué ser quien lo conserva |
| La exclusividad de Agora sobre ejecución IA durable puede leerse demasiado ampliamente | [ADR-AIOS-003](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:6597>) y [consulta durable de KO](<D:/Desarrollo/Proyectos TFM/Knowledge_Orchestrator/src/knowledge_orchestrator/api/openapi.py:77>) | Acotar exclusividad a Jobs del flujo integrado; preservar durabilidad propia de inferencias, consultas y Runs de sus dominios |
| Conviven mayúsculas/minúsculas y actores `deterministic`/`system` | [Actor Capability](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:993>) y [actor Task](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/OS-0.md:2733>) | Distinguir etiquetas de presentación y valores de transporte, y documentar el mapeo entre actores |

## Orden recomendado para mejorar el informe, sin desarrollar

1. **Reparar la fuente documental y su estado:** formato, referencias, denominaciones y distinción entre decisión propuesta, aprobada y futura.
2. **Cerrar el contrato maestro:** inventario, diccionario de datos, identidades nativas/globales, estados, autoridades y versiones. Sin generar todavía código de servicio.
3. **Resolver las decisiones de mayor impacto:** combinación de políticas, aprobaciones, aplicabilidad de certificaciones y modelo efectivo, snapshots de contexto y garantías de eventos/durabilidad.
4. **Contrastar cada integración:** contrato actual, diferencia requerida, propietario del adaptador, compatibilidad y alcance probado. Priorizar Agora y Model Drift por las diferencias verificadas; completar Broker con su fuente real.
5. **Sincronizar fases y prompts:** dependencias, alcance exclusivo, entradas y condiciones de cierre. Revisar la planificación y el despliegue antes de las fases de ejecución.
6. **Añadir ejemplos de aceptación en lenguaje natural:** comportamiento esperado y evidencia necesaria para cada fallo relevante. Su ejecución y automatización pertenecerían al desarrollo posterior.

Una revisión documental podría considerarse lista para aprobación cuando permitiera responder de forma inequívoca estos casos:

- El mismo comando llega dos veces simultáneamente y después vuelve a llegar tras un reinicio.
- Se recibe un evento anterior después del estado final de un recurso.
- El Core permanece apagado mientras otro servicio produce eventos.
- Una aprobación vence o la acción cambia antes de ejecutarse.
- El Broker hace fallback o cambia el modelo después de una comprobación de certificación.
- Una huella obtiene nueva información, pero no hay evidencia de cambio real de modelo.
- KO cambia un documento o expira un paquete mientras un Run histórico debe seguir siendo auditable.
- Varios Jobs de una Task terminan con resultados distintos.
- Una tarea híbrida necesita intervención al principio y al final, y dos trabajos compiten por una GPU.
- Un servicio intenta registrar otro propietario, consultar un recurso no autorizado o inducir una petición HTTP fuera de su ámbito.

## Verificaciones realizadas y límites

- Lectura de todos los archivos originales y contraste cruzado de OS-0, OS-1 y prompts.
- `manifest.json` es JSON válido; todos sus archivos existen; el orden recomendado no referencia archivos ajenos al manifest ni repite entradas. Esto confirma integridad del paquete, no coherencia semántica de las fases.
- Comprobación estática del formato y parseo YAML de OS-0: 41 bloques, 39 errores en su forma literal. Los dos que parsean no quedan por ello acreditados como contratos completos.
- Inspección selectiva de código y documentación de aplicaciones existentes, con enlaces directos en este informe. No se han arrancado aplicaciones, efectuado inferencias ni ejecutado las suites de los repositorios.
- Contraste técnico con documentación oficial de SQLite, especificaciones de ULID/canonicalización y guías primarias de OWASP.
- Se han conservado los 20 originales. La única entrega añadida al proyecto es este informe de revisión; no se han creado servicios, contratos ejecutables ni cambios de integración.

**Decisión recomendada:** conservar la arquitectura propuesta y revisar sus contratos antes de declararlos congelados. La siguiente actividad debe seguir siendo documental: resolver las decisiones identificadas y actualizar de forma coherente OS-0, OS-1 y el kit de prompts.
