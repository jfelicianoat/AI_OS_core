# AI OS Core — Control Plane (M0) · v0.4.2

Control plane determinista, federado y local-first para la plataforma AI OS.

## Responsabilidades
- **Goals & Objectives**: Gestión jerárquica de metas e intenciones globales.
- **Service & Capability Registry**: Registro seguro con validación SSRF y allowlists.
- **Resource Graph & Identity Binding**: Proyección y mapeo federado de identidades entre sistemas heterogéneos.
- **Event Store & Inbox**: Ingesta idempotente, ordenamiento de secuencias por epoch, detección de `REPLAY_GAP` y cuarentena ante divergencias de estado (`state_digest`).
- **Policy Engine (Base M0)**: Evaluación de lógica ternaria (`TRUE`, `FALSE`, `UNKNOWN`) bajo modos `all` y `any`, y resolución de precedencia (`DENY > REQUIRE_APPROVAL > INDETERMINATE > ALLOW`).
- **Restore & Idempotencia**: Comprobantes de operación (`OperationReceipt`) y resolución de reintentos concurrentes sin duplicación de efectos.

## Requisitos
- Python 3.11+
- FastAPI, Pydantic v2, Uvicorn (opcional para ejecución REST; el core incluye modo desacoplado estándar)

## Ejecución y Pruebas
### Ejecutar pruebas con pytest o unittest:
```bash
python -m unittest discover -s tests
```
O con pytest:
```bash
pytest -v
```

### Iniciar el servidor localmente:
```bash
uvicorn ai_os_core.app:app --host 127.0.0.1 --port 8000 --reload
```
`run.bat app` arranca Core y abre el monitor en el navegador: `http://127.0.0.1:8000/monitor`.

### Base de datos
Por defecto `%LOCALAPPDATA%\AIOSCore\data\ai_os_core.db`; se cambia con `AI_OS_DB_PATH`.
Los tests redirigen siempre a un fichero temporal (`tests/__init__.py`): nunca tocan la base real.
Otros ajustes: `AI_OS_ALLOWED_HOSTS` (hosts DNS extra admitidos en el registro), `AI_OS_ALLOW_PRIVATE_NETS` (por defecto `true`).

## Cambios 0.2.1 (pruebas 2026-10-18)
Sondeo de las 49 rutas (cuerpos vacíos, tipos y valores límite) y de sus escenarios, más el E2E real con Broker y Agora (31 comprobaciones). Defectos corregidos, cada uno con su test en `tests/integration/test_api_regressions_0_2_1.py` (comprobado que falla con el código anterior):
- Enteros ≥ 2⁶³ (revisiones, secuencias…) daban 500: ahora 400.
- Recibos de operación: el estado sólo avanza; un terminal no se reescribe y otro receptor no puede pisarlo (antes un `not_seen` tardío convertía un `succeeded` en `retry_allowed` → reenvío duplicado).
- Planificador: un `ALLOW` sólo vale con el `trace_id` de una evaluación real de Core (`/policies/evaluate` lo devuelve ahora); sin decisión de política no se despacha. Antes bastaba escribir `{"authorization":"ALLOW","executable":true}`.
- Bandeja de eventos: el cursor sólo cuenta lo aplicado; al llegar la secuencia que faltaba se reanudan en orden los eventos retenidos y el REPLAY_GAP queda resuelto (antes el evento del hueco se perdía y el siguiente entraba sin él). Eventos de un epoch anterior: sólo auditoría. Mismo `event_id` con otro contenido → 409. `source_sequence` ≥ 1.
- Presupuesto: las consultas de cuenta y reserva aplican la caducidad (antes mostraban saldo retenido de reservas caducadas); reserva que nace caducada → 400.
- Registro: `health_status` ilegible → 400 (antes `healthy`); `service_id`/`name`/`capability_id` vacíos → 422.
- Certificaciones: sólo su `source_system` puede reescribirlas.
- Los 422 de validación usan el sobre de error común (`error` + `detail`).
- **Autenticación opcional**: con `AI_OS_API_TOKEN` definido, toda la API exige `Authorization: Bearer <token>` (401 si falta); `/health`, `/ready` y la documentación siguen públicas. Sin la variable, todo queda como en 0.2.0.
- **Tokens por app**: `AI_OS_API_TOKENS="chatygpt=token1;athena=token2"`. Cada token fija quién llama: declarar otro principal en `X-Principal-Id` o en el `principal_id` del cuerpo → 403, y las claves de idempotencia se separan por app. Se puede combinar con `AI_OS_API_TOKEN`.
- **Permisos por token**: `app=token|scope1,scope2|CLEARANCE` limita qué scopes y qué nivel de clasificación puede pedir esa app al planificador y a los paquetes de contexto (pedir más → 403). Un nivel mal escrito impide arrancar.

### Primera app dirigida de verdad: Gestión Tareas IA 1.49.0
La app consulta a Core por sí misma (Conexiones › AI OS Core): antes de mandar trabajo al Broker evalúa la política `gestion_tareas:broker` y sólo envía con un ALLOW ejecutable (si Core no contesta, no envía), y le manda los recibos de cada estado. Verificado con su `scripts/verify_ai_os_core.py` (11/11): su `SubtaskSplitService` real, este Core con tokens por app y el Broker real — DENY no envía nada, ALLOW divide una tarea real y deja el recibo `succeeded` enlazado a la tarea del Broker, Core caído no envía nada.
- Certificaciones de modelos del Broker (`proveedor/despliegue/modelo`): la consulta `GET /certifications/{model_id}/{capability_id}/{version}` admite barras en `model_id` (antes daba 404 y la certificación era ilegible).

### Pruebas con el resto de apps
Antes de 0.2.2 ninguna otra app llamaba a Core; estos recorridos la simulaban desde fuera (ambos verdes el 18-oct con el token activo):
- `scripts/e2e_broker_agora.py` (31): tarea LLM real en el Broker y proyección del tablero de Agora.
- `scripts/e2e_ecosistema.py` (33): certificaciones a partir de los resultados reales de Model_Drift, elección del modelo de Athena según esas certificaciones (`muse-glimmer:latest` autorizado; `qwen3.8:27b` y `lfm2:24b` descartados), run real de Athena sobre el Broker gobernado por Core, y proyección de las 76 tareas de una copia de Gestión Tareas IA con su estado canónico idéntico al origen.
- `scripts/e2e_resto_apps.py <core> <carpeta_copias>` (18): copias de las bases de ChatyGPT, Knowledge Orchestrator, Trading AI desktop y Local AI Lab. Core recomienda la acción correcta tras una caída para las 4 293 tareas al Broker de ChatyGPT y las 235 de KO (incluidas las que siguen en cola o en curso), y proyecta sus conversaciones, flujos, 11 backtests y 10 registros de experimentos con el estado canónico idéntico al origen. Verde también con Core arrancado sólo con tokens por app.
- LARM no entra en ningún recorrido: hoy sólo es especificación y prompts, no hay programa que gobernar.

## Cambios 0.4.2: el monitor ve todo el tráfico con la API de Core (2026-10-20)
Hasta ahora el monitor sólo veía las consultas de política, los recibos y los saltos que cada app
declaraba. Las demás llamadas de las apps a Core (pedir el token del Broker, publicar
certificaciones, enviar eventos, proyectar recursos, el planificador…) no se veían.
- Cada llamada de una app a `/api/...` queda como paso `api` (app → Core): método, ruta, código de
  respuesta, bytes enviados y recibidos (`bytes_in`/`bytes_out`, de `Content-Length`) y latencia.
  Nunca el cuerpo. Va en el flujo de su `X-Flow-Id` si lo trae; si no, en el flujo del día de esa
  app (`api_<app>_<AAAAMMDD>`). Una llamada idéntica a la anterior del mismo flujo no se repite
  (el runner de Agora publica el token del Broker cada minuto).
- No se anotan otra vez las que ya tienen paso propio (`/policies/evaluate`, `/operations/receipts`,
  `/flows/...`) ni las que no dicen qué app son (el director y el propio monitor, que sondean).
- En el monitor: color propio («datos con Core»), viaje de ida y vuelta a Core (rojo si responde
  ≥ 400), frase en el relato con lo enviado y recibido, y «Datos movidos» en el detalle de cada flujo
  (suma también los `bytes_in`/`bytes_out` que las apps pongan en `details` de sus saltos).
- ChatyGPT 0.4.12 informa además de sus lecturas a Knowledge Orchestrator (`chatygpt_ko_<uuid>`).
- Test: `tests/integration/test_flows_monitor.py::test_api_calls_of_an_app_are_recorded_as_steps`.

## Cambios 0.4.0: ningún token pegado a mano (2026-10-19)
Antes había que pegar en cada app su token de Core y el token del AI Broker, que además cambia cada vez que el Broker arranca. Ahora:
- **Token de cada app con Core: lo genera Core.** Al arrancar, Core crea (una sola vez) un token para el director y para cada app de `conexion.PRINCIPALS` y lo deja, con su URL, en `%LOCALAPPDATA%\AIOSCore\conexion\<app>.json`. Las apps lo leen de ahí si no se lo pasa el lanzador. Un token fijado en `AI_OS_API_TOKEN(S)` manda sobre el generado. El token sigue siendo **uno por app** (fija quién llama, 403 si una app firma como otra): no hay un token común para todo. `AI_OS_AUTO_TOKENS=false` lo desactiva y `AI_OS_CONNECT_DIR` cambia la carpeta.
- **Token del Broker: lo reparte Core.** El runner de Agora vive junto al Broker en el PC IA y lee del llavero el token que el Broker publica al arrancar. Se lo envía a Core (`PUT /api/v1/credentials/broker`; sólo el principal `agora` o el director, el resto 403) cuando cambia, y cada minuto por si Core se ha reiniciado: Core lo guarda **sólo en memoria**. Las apps lo piden (`GET /api/v1/credentials/broker`, 503 si aún no ha llegado). Si el Broker les responde 401/403, lo vuelven a pedir y repiten la petición una vez.
- **HTTPS en la red.** `python -m ai_os_core.serve` (lo usa `run.bat`) sirve siempre `http://127.0.0.1:8000` para este equipo. Con `AI_OS_HOST` distinto de 127.0.0.1 abre además `https://<host>:8443` (`AI_OS_TLS_PORT`) con el certificado del tablero de Agora (`C:\Agora\pki\server.crt`/`.key`, o `AI_OS_TLS_CERT`/`AI_OS_TLS_KEY`), firmado por la CA en la que el runner ya confía. El 8000 ya no escucha en la red: por la red no viaja ningún token en claro. Sin certificado, Core se niega a abrirse a la red.
- **Monitor sin pegar el token.** Core abre el monitor cuando ya contesta, con el token del director tras `#token=`: el navegador no lo envía a ningún servidor, la página lo guarda y lo borra de la barra de direcciones.
- `Abrir Core a la red.bat` abre ahora el 8443 (rehace la regla del 8000) y genera el «Conectar runner a Core.bat» con la URL `https://`. Ya no hay que pegar el token de Gestión Tareas IA.

Apps que toman su conexión de Core y le piden el token del Broker: Model_Drift 0.4.2, Athena 0.3.4, Knowledge Orchestrator 0.4.6, Local AI Lab 0.1.3 (escritorio 0.1.4), Trading AI 1.3.2, Gestión Tareas IA 1.49.2 y ChatyGPT 0.4.9. El runner que publica el token es Agora 0.2.15.
Tests: `tests/integration/test_conexion_credenciales.py` (3). Recorrido real del 19-oct, 12/12: Core arrancado con HTTPS en la red, HTTP no alcanzable desde la red, HTTPS rechazado sin la CA de Agora, runner publicando por HTTPS, otra app no puede cambiar el token (403), y las seis apps en Python empezando con un token caducado: el Broker real del PC IA responde 403, la app pide el token a Core y el Broker la acepta.

## Cambios 0.3.1: parar apps y arreglos del monitor (2026-10-19)
- **Botón «Parar» por app** en «Aplicaciones» (`POST /api/v1/apps/{id}/stop`). Cierra con `taskkill /T` los procesos cuya línea de comandos contiene alguna marca `match` de la app (con sus hijos: la consola del `.bat`, el python…). Nunca toca el proceso de Core. Si otra app en marcha la necesita (`requires`), la página avisa de cuál y pide «Parar igualmente» (`?force=true`; sin él, 409). Sólo el token director (o, sin tokens, este equipo). Remota o sin `match` → 400.
- **Conexiones zombi del monitor:** detrás de los middleware HTTP de Core no llega la desconexión del navegador, y una pestaña cerrada dejaba su conexión viva hasta 10 min, bloqueando recargar o parar Core. Ahora cada conexión dura 30 s (`AI_OS_MONITOR_MAX_S`) y la página reconecta sola desde el último paso, sin avisar.
- **Consolas vacías:** al lanzar un `.bat`/`.cmd` con `start`, Windows usa `cmd /K` y la consola se quedaba abierta al acabar. Se lanzan con `cmd /c`.
- Las apps del catálogo toman de él su nombre e icono en la constelación (antes, si se veían antes que el catálogo, salían como «sin registrar»). La hora del relato lleva siempre dos cifras.
- `Arrancar AI OS Core.bat`: arranca Core y abre el monitor (lo mismo que `run.bat app`).
- `Abrir Core a la red.bat` (pide administrador): crea los tokens que falten (director, `agora`, `gestion_tareas`) como variables de entorno del usuario, pone `AI_OS_HOST=0.0.0.0`, abre el puerto 8000 solo a la red local y genera `dist\Conectar runner a Core.bat`, que en el PC IA actualiza el runner con `-CoreUrl`/`-CoreToken` y vuelve a registrar su tarea. Con `-Deshacer` quita `AI_OS_HOST` y la regla del firewall; con `-Prueba` no toca el sistema.
- Recorridos reales del 19-oct (Core de pruebas con token por app y Broker real): Athena 9/9, Model_Drift 12/12, KO 7/7, Local AI Lab 7/7, Trading AI 6/6, Agora 9/9, Gestión Tareas IA 11/11, ChatyGPT 3/3 y el recorrido completo ChatyGPT → Athena → Core → Broker → Athena → ChatyGPT (`cargo test --lib real_chatygpt_athena -- --ignored`).

## Cambios 0.3.0: monitor visual (2026-10-18)
`/monitor` es una página servida por Core que enseña en vivo qué pasa en el ecosistema:
- **Constelación**: Core en el centro, las apps en anillo y el Broker fuera. Cada mensaje es un destello que viaja entre nodos con el color de su tipo: petición, consulta a Core, autorizada o denegada, respuesta o recibo. El anillo se recoloca solo cuando aparece una app nueva. Una app que llama sin estar registrada en Core (ni token ni políticas) sale en rojo como «sin registrar».
- **Relato**: columna lateral con cada petición en frases cortas y su estado (en curso, completada, denegada, con error, solo consulta).
- **Detalle**: al pulsar una petición se abre su diagrama de secuencia con la política aplicada, la clasificación del dato, el modelo, los tiempos y el recibo.
- Iconos de cada app y fondo de nebulosa generados con Magnific (`src/ai_os_core/monitor/`). Para una app nueva basta con dejar `iconos/<principal>.svg`; si no hay, usa `desconocida.svg`.

Cómo llega la información (sólo metadatos, nunca el texto de la petición; `details` ≤ 4 KB):
- Cada petición lleva un `flow_id` que viaja de app en app (cabecera `X-Flow-Id`).
- Las apps informan de cada llamada que hacen a otra: `POST /api/v1/flows/hops` con `{flow_id, source_system, target_system, kind: request|response|error, summary, details}`. `source_system` es siempre quien informa (con token por app, 403 si no). `response` y `error` se refieren a la respuesta que esa app recibe de `target_system`. Informar nunca debe frenar a la app: es «enviar y olvidar».
- Core anota por su cuenta las evaluaciones de política (`context.flow_id`) y los recibos (`evidence.flow_id`). Sin `flow_id`, quedan como un flujo suelto con su `trace_id` u `operation_id`, así que las apps sin actualizar también se ven. Un paso idéntico al último del mismo flujo (mismo tipo, app y resumen) no se repite: el runner de Agora vuelve a preguntar por cada tarjeta pendiente en cada vuelta y no debe inundar el monitor.
- Lectura: `GET /api/v1/flows/events`, `GET /api/v1/flows/{flow_id}`, `GET /api/v1/flows/apps` y `GET /api/v1/flows/stream` (Server-Sent Events, sondeo de SQLite cada `AI_OS_MONITOR_POLL_S`=0.5 s; cada conexión dura como mucho `AI_OS_MONITOR_MAX_S`=30 s y la página reconecta sola desde el último paso; es corto porque detrás de los middleware de Core la desconexión del navegador no llega y, sin tope, una pestaña cerrada dejaba la conexión viva bloqueando recargar o parar Core). La página y los iconos son públicos y no llevan datos; los datos piden el token (la página lo pide una vez y lo guarda en el navegador).
- Demostración sin las apps: `python scripts/demo_monitor.py <core>` (tras `sembrar_ecosistema.py`).

**Lanzador** (pestaña «Aplicaciones» del monitor). Muestra qué apps están en marcha y deja arrancar las que no, respetando sus dependencias. Al abrir el monitor con apps paradas, empieza en esa pestaña. Las apps paradas salen atenuadas en la constelación, y pulsar un nodo lleva a su fila.
- Catálogo: `config/apps.json` (u otro con `AI_OS_APPS_FILE`). Por app: `start` y `cwd` (cómo se arranca), `health` (una URL que conteste) o `match` (un trozo de la línea de comandos de su proceso), `requires` (sin ellas vivas no se puede arrancar; p. ej. Gestión Tareas IA necesita el tablero de Agora), `uses` (las usa; sólo avisa) y `env`, donde `{core_url}` y `{token}` (el de esa app en `AI_OS_API_TOKENS`) se rellenan al arrancar: la app queda conectada a este Core sin configurar nada. Una app nueva es una entrada más.
- `GET /api/v1/apps` da el estado; `POST /api/v1/apps/{id}/start` arranca (202). 409 si ya está en marcha o le falta una dependencia, 400 si es remota (el Broker vive en el PC IA), 404 si no está en el catálogo. Sólo el token común (director) arranca apps: el token de una app → 403; sin tokens configurados, sólo desde el propio equipo. Core sólo ejecuta lo que dice el fichero, nunca un comando que llegue en la petición.
- Cada arranque se ve en el monitor como un paso Core → app. Estado de las apps de escritorio: procesos de Windows (`Get-CimInstance`, en caché 3 s).
- Tests: `tests/integration/test_launcher.py` (6; el arranque real se sustituye para no abrir ventanas).
- Tests: `tests/integration/test_flows_monitor.py` (7).

## Cambios 0.2.2: todas las apps dirigidas por Core (2026-10-18)
Cada app, antes de mandar trabajo al AI Broker, evalúa la política `<principal>:broker` con su
`data_classification`, y sólo envía con un ALLOW ejecutable; DENY, aprobación pendiente,
INDETERMINATE o Core caído → no se envía nada. Después deja recibos de operación
(`accepted` → `succeeded`/`failed_terminal`/`cancelled`). Sin URL de Core cada app funciona como antes.

| App (principal) | Dónde decide | Configuración | Recorrido real |
|---|---|---|---|
| Gestión Tareas IA 1.49.0 (`gestion_tareas`) | `CoreGovernedBrokerClient` | Conexiones › AI OS Core | `scripts/verify_ai_os_core.py` 11/11 |
| Model_Drift 0.4.0 (`model_drift`) | por tirada; publica certificaciones `suite:<id>` | `core_url` / `MODEL_DRIFT_CORE_URL`, `MODEL_DRIFT_CORE_TOKEN` | 12/12 |
| Athena 0.3.2 (`athena`) | `RunRegistry.start/resume` (servicio y escritorio; 403/503) | `ATHENA_CORE_URL`, `ATHENA_CORE_TOKEN` | 9/9 |
| Agora 0.2.13 (`agora`) | runner, antes de reclamar la tarjeta | `--core-url`, `AGORA_CORE_TOKEN` | 9/9 |
| Knowledge Orchestrator 0.4.3 (`knowledge_orchestrator`) | `BrokerClient.create_task` | `KO_CORE_URL`, `KO_CORE_TOKEN` | 7/7 |
| Local AI Lab 0.1.1 (`local_ai_lab`) | `BrokerTaskClient.invoke` | `LOCAL_AI_LAB_CORE_URL`, `LOCAL_AI_LAB_CORE_TOKEN` | 7/7 |
| Trading AI 1.2.2 (`trading_ai`) | `BrokerAIClient.create_task` | `TRADING_AI_CORE_URL`, `TRADING_AI_CORE_TOKEN` | 6/6 |
| ChatyGPT 0.4.2 (`chatygpt`) | `BrokerClient::create_task` (Rust) | `CHATYGPT_CORE_URL`, `CHATYGPT_CORE_TOKEN` | `cargo test real_ai_os_core -- --ignored` 3/3 |

Puesta en marcha: arrancar Core con `AI_OS_API_TOKEN` (director) y `AI_OS_API_TOKENS` con un token
por principal, y crear las políticas base con `scripts/sembrar_ecosistema.py <core>` (por ámbito:
DENY si `restricted`, ALLOW base). Con token por app, `principal_id`, `source_system` y `producer_id`
del cuerpo tienen que ser los del token (403 si no): una app no puede certificar en nombre de Model_Drift.
El runner de Agora y los Workers de Local AI Lab viven en el PC IA: Core debe ser alcanzable desde allí.

## Cambios 0.2.0 (revisión 2026-10-07)
- C07/C09 bajo concurrencia real: las transacciones usan `BEGIN IMMEDIATE` (antes 10 reservas simultáneas de 80 sobre 100 aceptaban 3).
- Idempotencia HTTP con reserva atómica, namespace `principal + operación + clave`, 409 en conflicto o en curso.
- Duplicados → 409 (no 500); reentrega del mismo evento → `duplicate: true` sin reprocesar.
- Sin fallos en abierto: techo de autonomía inválido, política indeterminable, operador desconocido, `expires_at` ilegible y clearance inválido se rechazan o dan INDETERMINATE.
- `expected_digest` de las aprobaciones se aplica; revocación expuesta en la API.
- SSRF: bloqueo de link-local, IPv4 mapeada, 0.0.0.0, multicast e IPs públicas fuera de la allowlist.
- Nuevas rutas: alta de cuentas de presupuesto, reservas, objetivos por meta y su estado, auditoría de meta, listado de políticas, cuarentena de eventos, recibos de operación, grafo de recursos e identity bindings.
- Marcas de tiempo por instancia (antes todas compartían la hora de importación del módulo).

Manual de uso: `docs/Manual_de_uso_AI_OS_Core.pdf`.
