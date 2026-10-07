# Revisión de AI OS Core — Especificación normativa 0.5

Fecha: 12 de septiembre de 2026. Alcance: revisión de los doce archivos de `AI_OS_Core_Normative_Spec_0_5`, contraste con la especificación 0.4 y seguimiento de sus seis hallazgos. Sin desarrollo de la aplicación ni elaboración de prompts.

## Dictamen

**La 0.5 corrige gran parte de lo solicitado y mantiene una arquitectura favorable, pero todavía no recomiendo cerrar la especificación con un dictamen plenamente positivo.** Hay dos problemas principales: se han perdido reglas explícitas de acceso y seguridad al consolidar el texto, y la comprobación de aceptaciones todavía permite aprobar decisiones o artefactos que dependen de una aceptación invalidada.

No es una repetición íntegra del resultado anterior. La separación de las tres puertas es correcta; las inconsistencias reales de proveedores y perfiles están corregidas; los casos de admisión, los bordes de Policy, la restauración y el mínimo de autonomía están ahora mucho mejor definidos. Las diez pruebas incluidas se ejecutan correctamente.

Los pendientes se concretan en **dos hallazgos de prioridad alta y dos de prioridad media**. Los dos primeros justifican mantener `draft-reviewable`. Los restantes ayudan a conservar las decisiones ya tomadas y a delimitar con precisión la garantía del verificador. No se requiere rediseñar el sistema, añadir aplicaciones ni iniciar implementación para resolver la parte normativa.

| Dimensión | Estado comprobado |
|---|---|
| Separación entre candidata, aprobación y puerta P01 | Correcta |
| Catálogo de contratos | 57 nombres coincidentes entre texto y registro |
| Requisitos M0/M2 y perfiles | Corregidos en el contenido actual |
| Proveedores anteriores a verificación | Correctos en el grafo actual |
| Restauración por estado de operación | Corregida respecto a N04 |
| Bordes de Policy y autonomía | Corregidos respecto a N05/N06 |
| Conservación de reglas anteriores | Incompleta; se han perdido reglas de seguridad y otras decisiones |
| Validación de aceptación directa | Mejora sustancial |
| Invalidación por dependencias y concordancia de revisiones | Pendiente |
| Preparación para cerrar la especificación | Pendiente de los ajustes indicados |

Que las seis decisiones sigan propuestas y los nueve artefactos pre-P01 estén pendientes es legítimo. La especificación distingue correctamente estos estados de una valoración documental favorable. **La falta de aprobación humana o de documentos P00 materializados no es el motivo de este dictamen pendiente.**

## Comprobaciones realizadas

Se han leído los doce archivos, incluido el código del verificador y sus pruebas, antes de ejecutarlos. Se ha contrastado el contenido con la [revisión 0.4](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_NORMATIVE_SPEC_AI_OS_CORE_V0_4_2026-09-12.md>) y con las reglas de la fuente normativa anterior.

- Los ocho hashes incluidos en el manifest coinciden. Los archivos de estado y salida que no enumera son resúmenes derivados; no considero esa exclusión un defecto por sí misma.
- El texto y el registro contienen los mismos **57 contratos**, sin diferencias de nombres.
- Hay **31 requisitos**, **16 fases** y **26 casos de aceptación**.
- M0 contiene 11 requisitos; M2-minimal, 18; M2-contextual añade 2 al perfil mínimo.
- No hay ciclos en el grafo actual. Cada proveedor está en la misma fase que su comprobación local o precede transitivamente a su fase verificadora.
- En los datos actuales, las relaciones requisito–test coinciden en ambos sentidos. No se han encontrado IDs de decisiones o casos duplicados.
- El verificador real devuelve `CandidateConsistency: PASS`, `SpecApproved: NO`, `PreP01Ready: NO` y `RESULT: CONSISTENT_DRAFT`, con cero errores y una advertencia.
- Las **10 pruebas suministradas pasan**. Se reproducen las correcciones de las falsas aprobaciones básicas de 0.4.
- Se han añadido **11 comprobaciones diagnósticas independientes en memoria**: cinco controles y seis variantes deliberadamente defectuosas. No se han modificado las aceptaciones ni los archivos originales para realizarlas.
- La comprobación final de hashes conserva intactos los **107 archivos originales** registrados al comenzar esta revisión.

Las aprobaciones de los escenarios de prueba son datos sintéticos, identificados como tales. No son aprobaciones humanas del paquete. Tampoco se han ejecutado aplicaciones, inferencias, migraciones ni pruebas de integración del producto.

## Seguimiento de los seis hallazgos anteriores

| Hallazgo de 0.4 | Estado en 0.5 | Evidencia y límite |
|---|---|---|
| N01. Aprobaciones sin comprobar condiciones | Parcialmente resuelto | Ahora se leen aceptaciones, fuente y manifest; aprobar sólo flags falla. Faltan dependencias e igualdad con la revisión declarada por la propia decisión |
| N02. Registro no fiel a requisitos y proveedores | Resuelto en los datos actuales | M0 se amplía; P02/P03 y P03/P04 se distinguen; restore tiene proveedores previos; existen perfiles minimal/contextual |
| N03. Casos sólo nominales | Resuelto en los puntos concretos solicitados | C16/C17 cubren admisiones, C11 aplicabilidad, UI-M2 y M0-REG tienen resultados, C08 queda enlazado; la validación automática tiene el límite descrito en S04 |
| N04. Receipt no equivale a ejecución | Resuelto normativamente | Se separan EventDeliveryReceipt y estado/recibo de operación; accepted/in_progress no se reenvían; retención expirada da unknown |
| N05. Bordes de Policy | Resuelto normativamente | Vacío incondicional, restricciones incompatibles y aprobación con seguridad UNKNOWN tienen reglas y casos C18–C20 |
| N06. Autonomía incompleta | Resuelto en el mínimo solicitado | Se restituye authorization→certification→admission→ceiling, con executable, motivos y distinción bloqueado/A0 |

La mayoría de las correcciones pedidas sí se puede dar por incorporada en su dimensión documental. No recomiendo volver a discutir esas decisiones sin un motivo nuevo.

## Hallazgos pendientes

### S01 — Alta: han desaparecido reglas de acceso y seguridad de la fuente normativa

**Regresión documental comprobada.** La 0.5 se declara [única fuente normativa de arquitectura](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/NORMATIVE_SPEC_0_5.md:8>) y relega la 0.4 a referencia histórica. Sin embargo, elimina reglas que la versión anterior ya había concretado:

| Regla anterior | Referencia 0.4 | Situación en 0.5 |
|---|---|---|
| DENY por defecto para mutaciones, administración, acciones sensibles y lecturas sin scope | [Policy](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:154>) | No se determina el resultado por defecto cuando ninguna Policy concede permiso |
| El techo solicitado no autoriza; el efectivo depende de principal, Policy, destino/capacidad y petición | [Autorización](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:356>) | Se conserva `classification` como dato y `AuthorizationPrincipal` como nombre, pero no esta regla |
| Allowlist de registro por identidad de servicio y restricciones de destino, redirecciones y tamaño/tiempo | [ServiceRegistration](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:369>) | No se trasladan sus condiciones normativas |
| No reenviar credenciales a otro destino | [Credenciales](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:377>) | Regla ausente |

La exigencia de una futura Authorization Matrix y el caso UI-M2 que prohíbe revelar recursos no autorizados no sustituyen estas decisiones. La matriz necesitará precisamente una norma para decidir quién está autorizado, y las restricciones de registro afectan también a operaciones ajenas a la UI.

**Consecuencia concreta:** ante una mutación sin Policy aplicable o una petición que solicita una clasificación superior a la del principal, la 0.5 ya no proporciona la respuesta explícita que daba la 0.4. No afirmo que ordene permitir esas operaciones; afirmo que ha perdido la regla que impedía interpretaciones distintas.

**Corrección:** restituir estas reglas en la fuente 0.5. También sería válido incorporar expresamente un anexo normativo con revisión exacta y precedencia clara. Una referencia genérica a documentos históricos no basta. Si se desea cambiar alguna regla, registrar el cambio como decisión, con su nueva semántica.

**Cierre verificable:** quedan inequívocos los resultados de una mutación sin permiso, una petición con techo superior al autorizado y un registro/redireccionamiento fuera del destino permitido. Se conservan las garantías anteriores sin depender de instrucciones futuras.

### S02 — Alta: las aceptaciones no se validan hasta sus dependencias ni contra todos los datos de revisión

**Error reproducido de la herramienta documental.** El [modelo de aceptación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/NORMATIVE_SPEC_0_5.md:428>) conserva `depends_on`, `invalidates_if_changed` e invalidación de consumidores. La puerta de aprobación exige que no exista aceptación invalidada. El verificador comprueba el estado directo de las seis aceptaciones de decisión, pero no recorre sus dependencias ni las de los artefactos pre-P01.

Hay además una discordancia de revisión: las decisiones del registro declaran `artifact_revision` y `artifact_hash`, pero las comprobaciones comparan la aceptación con el hash global de la fuente, sin contrastarla con esos campos de la propia decisión. Véanse la [validación directa](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/verify_spec.py:188>) y las [funciones de aprobación y pre-P01](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/verify_spec.py:212>).

| Variante sintética | Resultado observado | Resultado exigible |
|---|---|---|
| D-POLICY aceptada, con dependencia explícita de una aceptación de contrato `invalidated` | `SpecApproved: YES` | No aprobar una decisión dependiente hasta resolver o reaceptar esa dependencia |
| Decisión que declara revisión 0.4/hash distinto, con aceptación que declara 0.5/hash actual | `SpecApproved: YES` | Detectar la discordancia entre el objeto aprobado y su aceptación |
| Nueve artefactos con archivos y hashes válidos, pero DOC-FIXTURES depende de una aceptación de contrato `invalidated` | `PreP01Ready: YES` | Mantener cerrada la puerta mientras esa aceptación consumidora no sea vigente |

Para aislar la causa, los hashes del manifest de cada variante virtual se actualizaron como hacen las pruebas suministradas. No se cambió el verificador. Todos los casos anteriores devolvieron cero errores. La prueba suministrada de aceptación directamente invalidada sí falla correctamente; el hueco está en las dependencias y en la concordancia del objeto referenciado.

**Corrección:** definir referencias de dependencia inequívocas y validar su vigencia transitiva. Una dependencia invalidada, ausente o incompatible debe impedir que el consumidor conserve una aprobación utilizable. Comparar también ID, revisión y hash de decisión, aceptación y fuente correspondiente. Para pre-P01 debe quedar explícito con qué revisión normativa son compatibles los artefactos: la mera existencia de un hash de archivo no demuestra esa compatibilidad.

No es necesario inventar una detección automática de toda incompatibilidad semántica. Puede declararla la revisión humana; la herramienta debe respetarla una vez registrada. Tampoco es necesario invalidar por un cambio editorial declarado compatible.

**Cierre verificable:** los tres casos anteriores dejan de habilitar su puerta; los controles con aceptaciones vigentes siguen funcionando. Se comprueban dependencias encadenadas y referencias inexistentes. No se exige una firma criptográfica ni un sistema externo de aprobación.

### S03 — Media: la reducción del texto ha dejado otras decisiones anteriores sin destino explícito

Además de seguridad, hay contenido ya definido en 0.4 que no se traslada ni se marca como retirado o diferido:

| Área | Decisión perdida o reducida | Acción documental sugerida |
|---|---|---|
| Identidad y revisiones | Distinción de versiones, conservación de IDs nativos y revisión durable del adaptador cuando falta una nativa | Recuperar la regla; enumerar nombres de contratos no define cómo se versionan sus datos |
| Aprobaciones | Vínculo único autorización–operación y detalle de exact_action frente a scoped | Conservar los invariantes; los campos completos pueden concretarse en el diccionario previsto |
| Idempotencia | Escritura atómica de operación Core y registro idempotente cuando comparten DB | Restituir esta decisión de persistencia ya tomada |
| Contexto | Instante de recuperación/validez al usar, separación entre caducidad de uso y retención histórica, exclusiones seguras frente a auditoría privilegiada | Precisar el significado de `validity` y preservar las distinciones necesarias para C12 |
| Dependencias de tareas y artefactos | Aciclicidad de dependencias bloqueantes; separación de autoridad, productor y custodio del artefacto | Mantener las reglas o declarar su alcance diferido |
| Planner y etapas posteriores | Propiedad de PlanningService y límite que impide a Core crear Jobs directamente | Conservar el mínimo arquitectónico o excluir expresamente esta parte de la aprobación 0.5 |

Las referencias anteriores están en [identidad](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:96>), [aprobaciones](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:172>), [idempotencia](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:272>), [contexto](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:335>) y [tareas, artefactos e hitos](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:405>).

No considero que todo deba reproducirse con el mismo detalle ni que haya que diseñar M3–M6 ahora. El problema es que el lector no puede distinguir una simplificación editorial de una retirada de la decisión. La 0.5 conserva contratos y fases posteriores, por lo que tampoco declara inequívocamente un recorte de alcance a M0/M2.

**Corrección y cierre:** añadir una matriz breve de conservación: regla 0.4 → apartado actual, cambio deliberado o diferimiento explícito. Restaurar los invariantes de M0/M2 y acotar lo posterior. Esto evitará que la próxima revisión corrija un hallazgo eliminando accidentalmente otra decisión ya resuelta.

### S04 — Media: algunas garantías del verificador siguen siendo más estrechas que las reglas documentadas

**Limitación reproducida; los datos actuales sí son correctos.** La [norma prohíbe usar P10 como proveedor de M2](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/NORMATIVE_SPEC_0_5.md:417>). El [mapa de resolución](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/REVIEW_0_4_RESOLUTION_MAP.md:7>) afirma que el verificador cruza cobertura en ambos sentidos. Las pruebas independientes muestran estos límites:

| Cambio virtual | Resultado observado | Comprobación que falta |
|---|---|---|
| M2-JOB declara P10-minimal como proveedor | Candidata PASS | Prohibición del rol proveedor para P10 |
| P10-minimal se queda sin dependencias | Candidata PASS | Que cada proveedor preceda a la verificación del perfil |
| Se elimina C20 de los tests de M0-POLICY-BASE, pero C20 sigue declarando que lo cubre | Candidata PASS | Concordancia inversa de cada enlace `covers` con la lista del requisito |

El verificador comprueba que las fases nombradas existan y que el grafo no tenga ciclos; no comprueba todas las relaciones de precedencia exigidas. Para tests comprueba que cada test asignado declare cubrir su requisito, pero en el sentido contrario sólo exige que el requisito nombrado exista. Véanse [fases y referencias](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/verify_spec.py:101>) y [cobertura](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/verify_spec.py:156>).

**Corrección:** añadir estas comprobaciones estructurales concretas o describir expresamente la revisión manual que las sustituye, sin afirmar que ya se automatizan. La inspección independiente de esta entrega sí confirma que sus proveedores, dependencias y enlaces actuales son correctos.

Un campo `expected` no vacío y una relación `covers` demuestran trazabilidad declarada, no que el escenario pruebe semánticamente toda una función. Mantener esta distinción en la guía: la cobertura funcional la revisa una persona y, posteriormente, se contrasta con pruebas implementadas. No recomiendo intentar convertir el verificador en una certificación automática de toda la arquitectura.

**Cierre verificable:** los tres escenarios se rechazan por su causa específica, o quedan explícitamente fuera del resultado automático y sujetos a una comprobación manual identificada. Los diez self-tests existentes se conservan; son útiles, pero no exhaustivos.

## Observaciones que no considero bloqueos adicionales

- La definición de restore ha mejorado de forma suficiente para esta etapa: distingue recepción y ejecución, contempla operaciones en curso y declara horizontes de retención. No pido implementar receptores ni simular efectos reales ahora.
- Los nuevos C16/C17 y C18–C20 responden a las solicitudes anteriores. La falta de código de esas pruebas es coherente con una entrega de especificaciones.
- Los artefactos pre-P01 pueden tener revisión propia distinta de la versión de la spec. Lo necesario es una relación de compatibilidad/aceptación vigente, no imponer que todo archivo se llame «0.5».
- La [regla de certificación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_5/NORMATIVE_SPEC_0_5.md:307>) permite excepciones explícitas por Policy para estados concretos. Conviene destacarlo como decisión funcional al aprobarla y documentar qué Policy permite cada excepción. No lo califico automáticamente como error: la excepción está escrita, aunque `mandatory` debe interpretarse junto con ella.
- El estado real sigue siendo candidata pendiente de aprobación. Las salidas positivas creadas dentro de self-tests no alteran ese estado ni justifican cambiar las aceptaciones de la entrega.

## Próximo cierre propuesto

Para una siguiente revisión, recomiendo una corrección acotada:

1. Recuperar las reglas de seguridad de S01 y comprobar conservación del resto mediante la matriz de S03.
2. Cerrar invalidación y concordancia de revisión de S02, con sus escenarios diagnósticos.
3. Ajustar las comprobaciones o el alcance declarado del verificador según S04.
4. Regenerar hashes y salidas una vez que el paquete definitivo esté coherente.

Así se preserva lo que la 0.5 ya ha resuelto. **La siguiente entrega puede seguir siendo exclusivamente documental.** Una vez corregidos los dos problemas prioritarios y delimitadas las observaciones medias, podrá revisarse el cierre sin exigir previamente aplicaciones funcionando, prompts de desarrollo ni aprobación humana ficticia.
