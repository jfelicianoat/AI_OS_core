# Revisión de AI OS Core — Especificación normativa 0.4

Fecha: 12 de septiembre de 2026. Alcance: los ocho archivos de `AI_OS_Core_Normative_Spec_0_4`, su coherencia interna y el seguimiento de la revisión v0.3. Revisión de especificaciones, sin desarrollo de la aplicación ni elaboración de prompts.

## Dictamen

**La arquitectura merece una valoración favorable, pero todavía no doy un informe positivo de cierre de la especificación.** La 0.4 mejora sustancialmente la versión anterior: concentra las decisiones, delimita el MVP y resuelve varias ambigüedades operativas. No recomiendo rediseñar el sistema ni añadir componentes.

Los principales problemas pendientes están en la correspondencia entre lo que exige el texto y lo que comprueban el registro y el verificador. He reproducido aprobaciones automáticas sin evidencia de aceptación, encontrado requisitos normativos que no están representados fielmente y comprobado que varias pruebas citadas no verifican la función a la que se asignan.

Además, conviene precisar tres aspectos del diseño: el estado de ejecución que permite reenviar tras una restauración, ciertos resultados de Policy y la decisión efectiva de autonomía. Son lagunas documentales; no afirmaciones de fallos observados en una aplicación.

**Estado recomendado: conservar `draft-reviewable`, corregir estos puntos y volver a revisar la especificación antes de pasar a los prompts.** Las seis decisiones todavía propuestas y sus aceptaciones pendientes son un estado declarado legítimo, no un error por sí mismo. Este dictamen pendiente se debe a los hallazgos técnicos siguientes, no a la ausencia de una firma humana.

| Dimensión | Valoración |
|---|---|
| Arquitectura y reparto de responsabilidades | Favorable |
| Fuente normativa y catálogo de contratos | Coherentes en los archivos actuales |
| Aprobaciones y garantías de eventos | Mejoras sustanciales respecto a v0.3 |
| Registro de requisitos y dependencias | Incompleto respecto al texto |
| Cobertura de aceptación | Parcial; algunas asociaciones no prueban el requisito |
| Verificador como comprobación limitada de referencias | Útil |
| Verificador como autorización de cierre | No fiable todavía |
| Preparación para cerrar la especificación | Pendiente de los ajustes de este informe |

## Material y comprobaciones

Se han leído los ocho archivos: especificación, registro de requisitos, registro de aceptación, manifest, mapa de resolución, guía, verificador y salida guardada. Se han contrastado los ocho hallazgos de la [revisión v0.3](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/REVISION_ANALISIS_AI_OS_CORE_V0_3_2026-09-12.md>) y las decisiones anteriores relevantes para detectar pérdidas de contenido al consolidarlas.

Resultados comprobados:

- Los siete hashes de archivos incluidos en el manifest coinciden. Que el manifest no se incluya a sí mismo no es un defecto.
- El catálogo del apartado 3 y el JSON contienen los mismos **54 contratos**, sin diferencias de nombres entre ambos.
- El registro contiene **15 requisitos, 15 fases y 17 identificadores de casos**. El grafo declarado de fases no tiene ciclos.
- La ejecución real del verificador devuelve **`Errors: 0`, `Warnings: 1`, `CONSISTENT_DRAFT`**. La advertencia enumera las seis decisiones propuestas.
- Se han realizado nueve comprobaciones diagnósticas del verificador, incluida una base, seis variantes deliberadamente defectuosas y dos controles que sí deben fallar. Las variantes se suministraron en memoria: no se modificaron decisiones, aceptaciones ni archivos del paquete.
- Los controles detectaron correctamente un contrato desconocido dentro de un requisito y un ciclo de fases. Las limitaciones descritas abajo no significan que el verificador carezca de utilidad.
- Se han conservado los **94 archivos originales** registrados al comienzo de esta revisión; la comprobación final de sus hashes no detectó cambios.

La salida guardada contiene también un error de inicialización de un entorno de hojas de cálculo. No apareció al ejecutar aquí el verificador y no constituye evidencia de un problema de AI OS Core. Conviene separar ese ruido de entorno del resultado documental.

No se han ejecutado aplicaciones, inferencias, migraciones ni pruebas de integración. Las pruebas diagnósticas anteriores evalúan exclusivamente la herramienta de validación documental incluida en la entrega.

## Seguimiento de v0.3

“Resuelto normativamente” significa que la regla escrita responde al hallazgo, no que exista implementación ni aceptación humana.

| Hallazgo anterior | Estado en 0.4 | Evaluación |
|---|---|---|
| V01. Dos precedencias | Resuelto normativamente | Texto y JSON coinciden; los documentos anteriores quedan como referencia histórica |
| V02. Entregables previos incompletos | Resuelto en la definición de la puerta | Se enumeran los nueve artefactos; su existencia y aceptación futura son otra comprobación |
| V03. Dependencias E2E | Parcialmente resuelto | Presupuesto mínimo y proyección quedan situados en P02 en el texto; el registro conserva discrepancias |
| V04. Outbox «cuando sea posible» | Resuelto normativamente | Se distinguen garantía transaccional y recuperación sólo de estado final |
| V05. Aplicación de deltas | Resuelto para M0–M2 | Sólo `full_state` modifica la proyección; aplicar deltas queda expresamente diferido |
| V06. Aprobación y ejecución | Resuelto en la regla central | Uso y comando se comprometen juntos; se define concurrencia, reintento y efecto de la revocación posterior |
| V07. Restauración sin fase de prueba | Resuelto en la asignación de comprobación | Hay receptor simulado en M0 y comprobación real en M2; falta distinguir proveedor de función y verificador |
| V08. Aceptaciones por revisión e impacto | Resuelto como modelo, pendiente de validación | `AcceptanceRecord` define revisión e invalidación; la herramienta no las comprueba |

También están bien incorporadas la separación entre admisión de trabajo e inferencia, el significado de `confirmed` al iniciar y el presupuesto mínimo anterior a P13. La distinción entre certificación histórica y aplicabilidad actual, la evidencia de contexto reproducible y la separación de autoridades siguen siendo bases adecuadas.

## Hallazgos pendientes

Prioridad **alta**: afecta a la fiabilidad del cierre documental. Prioridad **media**: regla que debe concretarse, o diferirse con alcance explícito, antes de considerar cerrada la parte afectada. No se exige desarrollar las funciones para resolver estos hallazgos.

### N01 — Alta: el verificador puede declarar aprobación sin verificar sus condiciones

**Error reproducido.** La [guía](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/VERIFICATION_GUIDE.md:17>) condiciona `APPROVED_FOR_PROMPT_DERIVATION` a decisiones aprobadas y actualización del registro de aceptación. La [especificación](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:579>) impide continuar con aceptaciones invalidadas y exige revisión humana para el cierre.

Sin embargo, el [verificador](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/verify_spec.py:7>) sólo lee `spec_registry.json`. No lee el documento normativo, `acceptance_registry.json` ni el manifest. Su decisión final depende de errores locales y de los estados de las decisiones presentes en ese único JSON.

| Variante diagnóstica | Resultado observado | Limitación demostrada |
|---|---|---|
| Cambiar únicamente las seis decisiones a `approved` | `APPROVED_FOR_PROMPT_DERIVATION` | No exige aceptación, revisión ni evidencia; el registro real conserva sus seis `pending` |
| Dejar vacía la lista de decisiones | `APPROVED_FOR_PROMPT_DERIVATION` | No exige que existan las decisiones obligatorias |
| Vaciar los requisitos de M0 y M2 | `CONSISTENT_DRAFT`, cero errores | No comprueba cobertura mínima de los hitos |
| Sustituir la puerta pre-P01 por nueve nombres ficticios idénticos | `CONSISTENT_DRAFT`, cero errores | Comprueba longitud, no identidad ni unicidad de entregables |
| Invertir la precedencia declarada | `CONSISTENT_DRAFT`, cero errores | Detecta duplicados, pero no el orden normativo |
| Quitar `AcceptanceRecord` del catálogo JSON, manteniéndolo en el texto | `CONSISTENT_DRAFT`, cero errores | Sólo descubre contratos usados por los requisitos del propio JSON |

En estas comprobaciones cualquier intento de leer otro documento habría fallado deliberadamente; el verificador siguió funcionando porque nunca lo solicitó. No se trata sólo de una aceptación todavía sin rellenar: la herramienta puede emitir aprobación sin consultarla.

**Mejora:** exigir el conjunto obligatorio de decisiones y vincular cada aprobación a su revisión y evidencia de aceptación vigente. Comprobar los invariantes documentales que se anuncian, incluyendo correspondencia con la fuente normativa. El manifest puede servir para detectar diferencias de contenido, pero un hash coincidente no prueba aprobación ni corrección.

Separar tres resultados: coherencia de la especificación candidata, aprobación de esa revisión y cumplimiento de la puerta pre-P01. Esta última puede seguir pendiente mientras se aprueba el diseño; no hace falta exigir ahora esquemas o fixtures aún previstos como entregables posteriores.

**Cierre verificable:** ninguna de las variantes anteriores produce un resultado favorable que contradiga su alcance declarado. Una aceptación ausente, rechazada, invalidada o ligada a otra revisión no habilita la aprobación. La guía explica exactamente qué se comprueba automáticamente y qué requiere revisión documental.

### N02 — Alta: el registro no representa fielmente los requisitos y sus proveedores

**Incoherencias comprobadas.** El registro es internamente consistente en sus referencias, pero no equivale al contenido normativo.

1. **M0 pierde parte de su alcance.** El [apartado de M0](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:429>) exige Goals/Decisions/Resource Graph, idempotencia/auditoría, Policy base y proyección/consulta de CertificationApplicability. La [lista M0 del registro](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/spec_registry.json:180>) sólo incluye registry, approvals, budget, events y restore. Algunos aspectos aparecen indirectamente en casos, pero no hay trazabilidad completa de esos entregables.
2. **La proyección de certificación desaparece como entrega de P02.** El texto la exige expresamente en [P02](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:445>); `R-M2-CERT` señala únicamente [P03](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/spec_registry.json:292>). P03 puede integrar el servicio externo, pero eso no representa la entrega local previa.
3. **La restauración real vuelve a carecer de proveedor previo explícito.** El texto dice que P10 sólo verifica. El registro asigna `R-M2-RESTORE` a [P10 como `provider_phase`](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/spec_registry.json:382>). La fase que comprueba la integración no sustituye a las fases responsables de ofrecer consulta de estado en los receptores.
4. **Las funciones compartidas quedan reducidas a una sola fase.** Replay corresponde a P03–P07 en el texto y sólo a P03 en `R-M2-REPLAY`. La evidencia efectiva del modelo requiere P03/P04, pero `R-M2-MODEL` sólo indica P03. El registro no puede demostrar que cada productor o consumidor haya entregado su parte.
5. **El contexto es condicional en el texto y obligatorio en el grafo.** M2 requiere P07 «si aplica»; el registro incluye `R-M2-CONTEXT` sin condición y P10 depende siempre de P07. Falta declarar si se desea un único perfil con contexto obligatorio o un perfil mínimo que pueda prescindir de él.

**Mejora:** conciliar los requisitos con el texto, separando entregas por autoridad cuando sea necesario y distinguiendo fase proveedora de fase verificadora. Expresar la condición de aplicabilidad del contexto. No hace falta una fase nueva ni cambiar el reparto arquitectónico.

**Cierre verificable:** cada obligación M0/M2 tiene requisito identificable, propietario, entrega previa y criterio de aceptación. El registro permite demostrar que P10 verifica funciones ya suministradas y que el perfil mínimo elegido tiene exactamente las dependencias que anuncia el texto.

### N03 — Alta: citar un caso no acredita que cubra el requisito

**Deficiencia de cobertura comprobada.** La [matriz M2](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:493>) asocia contratos y pruebas, pero algunos casos no comprueban la capacidad asignada:

| Requisito | Caso asociado | Qué comprueba realmente | Qué falta definir |
|---|---|---|---|
| WorkerAdmission | C13 | Un Job fallido impide completar una Task `all_required` | Resultado cuando no hay capacidad y regla de concurrencia de admisiones |
| InferenceAdmission | C10 | Un modelo fuera de `{A,B}` no es válido | Admisión o rechazo por disponibilidad y capacidad de inferencia |
| CertificationApplicability | C11 | Enriquecer identidad no equivale automáticamente a cambiar modelo | Consulta de aplicabilidad actual y bloqueo por certificación obligatoria no vigente o indeterminada |
| UI trace | UI-M2 | Sólo existe su identificador | Escenario, evidencia visible y resultado esperado |
| Service/Capability registry | M0-REG | Sólo existe su identificador | Escenario y criterios de aceptación del registro |

Además, **C08 está definido y enumerado, pero no lo referencia ningún requisito**. Por ello, comprobar todos los tests enlazados desde requisitos no garantiza comprobar siquiera la obligación de aprobación ya descrita.

C10 usa «ejecución C no válida». La norma sí prohíbe el fallback fuera del conjunto obligatorio; el caso debería precisar que se impide invocarlo, no limitarse a calificarlo después, e incluir la evidencia del modelo realmente empleado.

**Mejora:** definir UI-M2 y M0-REG; añadir o ampliar escenarios que comprueben cada obligación anterior; enlazar Policy con C08. No es necesario que estos tests estén programados ahora: se necesitan entradas, condiciones y resultados esperados documentados.

**Cierre verificable:** una implementación que omita por completo admisión de workers, admisión de inferencia o bloqueo de certificación no podría satisfacer todos los criterios documentales de su requisito. No basta con que el identificador de test exista en una lista.

### N04 — Media: la restauración necesita distinguir recepción, ejecución pendiente y ausencia confirmada de efecto

**Ambigüedad de contrato.** El [protocolo de restauración](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:299>) manda consultar `receipt/status` y reenviar si la operación no se ha ejecutado. Sin embargo, la cobertura lo vincula a `EventDeliveryReceipt`, mientras que el inbox confirma la persistencia de un evento antes del ACK. No se define una equivalencia entre esa recepción y una prueba de ejecución del comando.

Ejemplo: el receptor aceptó la operación y sigue procesándola cuando se restaura Core. «Todavía no ejecutada» no significa necesariamente «ausente y seguro volver a enviarla». Tampoco encontrar un recibo de entrega demuestra que el efecto haya terminado. El texto contiene idempotencia, pero no precisa aquí la respuesta de reenvío de cada receptor ni cómo se interpreta este estado intermedio.

**Mejora:** definir normativamente la consulta de estado de operación, mediante un contrato específico o un contrato existente ampliado con semántica explícita. Debe distinguir efecto confirmado, operación en curso, ausencia confirmada que permite reintento y estado desconocido. Para una operación en curso se debe continuar su seguimiento; lo desconocido mantiene la reconciliación manual ya prevista. El reintento conserva identidad y el receptor declara su garantía de deduplicación y retención.

**Cierre verificable:** ampliar C15 con una operación recibida pero en curso y con un recibo que ya no está disponible. Esos escenarios no provocan un segundo efecto ni se confunden con un éxito final. No se exige implementar receptores en esta revisión.

### N05 — Media: faltan resultados explícitos para algunos casos de Policy

**Lagunas de determinismo.** La [semántica actual](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Normative_Spec_0_4/NORMATIVE_SPEC_0_4.md:106>) mejora la combinación por significado, pero deja tres bordes que conviene cerrar:

- **Condición incondicional vacía.** Se permite una lista vacía con `unconditional=true`, pero no se declara expresamente su resultado ni su precedencia sobre `condition_mode=any`. Conviene fijar TRUE para ambos modos, si ésa es la intención, y definir la validez de combinar ese indicador con condiciones no vacías.
- **Restricciones incompatibles.** Se definen mínimo de máximos y máximo de mínimos, pero no el resultado de obtener, por ejemplo, mínimo 100 y máximo 80 para la misma magnitud. La decisión v0.3 sí decía DENY ante incompatibilidad cierta e INDETERMINATE si dependía de UNKNOWN. Esa regla no está trasladada a la nueva fuente normativa.
- **Aprobación más incertidumbre de seguridad.** `REQUIRE_APPROVAL` precede a `INDETERMINATE`. La norma preserva obligaciones y dice que UNKNOWN de seguridad nunca da ALLOW, lo cual es adecuado. Falta precisar que satisfacer la aprobación no resuelve por sí mismo la incertidumbre pendiente ni habilita el commit mientras siga siendo bloqueante.

No afirmo que la especificación permita expresamente saltarse la seguridad; señalo que la decisión final no está descrita de forma inequívoca en esos escenarios.

**Mejora y cierre verificable:** añadir esos resultados y tres ejemplos de aceptación: `any` vacío e incondicional, intervalo imposible y aprobación obtenida con un dato de seguridad todavía desconocido. Dos lectores deben poder obtener la misma decisión sin completar reglas por intuición.

### N06 — Media: la consolidación ha perdido parte de la decisión de autonomía

**Pérdida de contenido normativo.** La [decisión v0.3 de autonomía](<D:/Desarrollo/Proyectos TFM/AI_OS_core/docs/AI_OS_Core_Prompts_v0_3/DECISION_AUTONOMY.md:6>) definía controles de autorización, certificación y admisión antes del techo A0–A5. También distinguía `executable=false`, `blocked_reasons` y un techo nulo; una acción bloqueada no equivalía a A0.

La 0.4 conserva el mínimo entre A0–A5, enumera `EffectiveExecutionDecision` y menciona «autonomía condicional» en M6. No incorpora aquella regla de composición ni la distinción bloqueado/A0. Como los documentos antiguos son ahora históricos y `D-AUTONOMY` figura entre las decisiones a aprobar, queda insuficientemente delimitado qué contenido se estaría aprobando.

**Mejora:** trasladar el mínimo normativo ya acordado a la 0.4 y vincular la decisión a ese apartado y revisión. No hace falta desarrollar ahora toda la autonomía M6. Si parte queda diferida, declararlo y limitar a lo realmente especificado el alcance de `D-AUTONOMY`.

**Cierre verificable:** un fallo de admisión produce una decisión no ejecutable con motivo, y no un nivel A0 interpretable como permiso. La aceptación identifica el contenido exacto aprobado.

## Ajustes complementarios

Estos puntos ayudan a formalizar P00; no los cuento como nuevos bloqueos de arquitectura:

- Tratar los seis registros `pending` actuales como borradores de aceptación. Al aceptar, exigir identidad de registro, revisión/hash, autor, fecha y evidencia; los campos todavía ausentes no deben completarse con aprobaciones inventadas.
- En las tablas de estados de presupuesto, precisar reserva, consumo, liberación y expiración durante una operación en curso. La reserva atómica inicial está bien especificada; el ciclo posterior debe conservar esa garantía.
- En la matriz de autoridad de eventos, precisar quién confirma una nueva época y el snapshot que establece el baseline. La decisión de excluir deltas del MVP reduce considerablemente la complejidad pendiente.
- Actualizar el mapa de resolución para distinguir «regla incorporada» de «verificación automática implementada». V03 y V08 no están cerrados en todas sus dimensiones.
- Mantener una salida del verificador limpia y reproducible, con versión del paquete y comando usado, separada de errores de herramientas ajenas.

## Condiciones para un siguiente dictamen positivo

El cierre puede hacerse enteramente en documentación y en la herramienta documental existente:

1. Corregir las falsas aprobaciones y ajustar la guía al alcance real de cada comprobación.
2. Conciliar M0/M2, proveedores, fases verificadoras y contexto opcional entre especificación y registro.
3. Definir los casos ausentes y la cobertura efectiva de admisión, certificación y Policy.
4. Precisar la semántica de estado de operación tras restore y los bordes de Policy indicados.
5. Restituir la regla mínima de autonomía o declarar explícitamente qué parte queda fuera de esta aprobación.

Una revisión documental favorable y la aprobación humana de una revisión concreta son pasos distintos. Tampoco equivalen a haber superado la puerta pre-P01 ni a una integración funcionando. **No hace falta iniciar desarrollo, completar aplicaciones externas o presentar prompts para resolver las observaciones de esta entrega.**
