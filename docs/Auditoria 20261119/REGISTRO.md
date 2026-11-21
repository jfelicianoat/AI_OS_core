# Auditoría del 19-nov-2026 · AI OS Core 0.4.4 → 0.4.6

Encargo: `instrucciones.md` (esta carpeta). Constructor: Claude. Árbitro: un agente independiente distinto (sólo lectura), ver §6.

## 1. Resumen

- **Resuelto:** cualquier app podía administrar Core (un DENY global de ChatyGPT dejaba sin Broker a todas), gastar el saldo de otra, cancelar sus metas o agotar sus aprobaciones; las políticas aceptaban cambios silenciosos, revisiones hacia atrás y gemelas; una app podía crear recursos a nombre de otra; los tests podían escribir en la base real; `run_local.ps1` abría HTTP sin cifrar a la red; el monitor enseñaba recorridos incompletos y el registro de pasos crecía sin límite.
- **Mejoras:** retención del monitor, detalle de flujos desde Core con tope, pantalla de token que explica dónde está el del director, pestañas con teclado, manual al día.
- **Incidente durante la auditoría (causado por el constructor):** al ejecutar `python -m unittest discover -s tests` (la orden del README) los tests escribieron en la base real y en `%LOCALAPPDATA%\AIOSCore\conexion`. Se reparó (§7) y es el defecto A-00.

## 2. Situación inicial (fase 1)

- Código 0.4.4; el informe del 14-nov decía 0.4.5 (A-07). Python 3.14 (`.venv`), FastAPI + SQLite WAL, migraciones 001–006, monitor HTML servido por Core.
- `pytest`: 109 verdes; `ruff`: limpio. `unittest discover -s tests` (README): 40 fallos y 15 errores, y contra la base real.
- Datos reales (copia): 75 861 pasos de monitor en un mes (36 MB), 14 792 trazas, 14 698 recibos, 23 políticas sin gemelas, restos de pruebas antiguas.
- Entorno real del usuario: Core en 127.0.0.1:8720 + 0.0.0.0:8443, `AI_OS_HOST=0.0.0.0`, tokens de director/agora/gestion_tareas en variables de usuario.
- Apps consumidoras (búsqueda en sus `src`): sólo usan `policies/evaluate`, `operations/receipts`, `flows/hops`, `credentials/broker`, `POST certifications` (Model_Drift) y `GET services`. Los guiones de verificación de otras apps crean políticas con el token del director.

## 3. Mapa funcional (objetivo → flujo → componentes → pruebas)

| Objetivo del usuario | Flujo | Componentes | Pruebas |
|---|---|---|---|
| Que una app sólo mande al Broker lo permitido | evaluar `<app>:broker` → ALLOW/DENY + turno → recibos | `policies.py`, `policy_service`, `restore.py`, `flows.py` | test_m0_cases, test_policy_semantics, recorrido E2E 21/21 |
| Gobernar el ecosistema (director) | políticas, aprobaciones, registro, metas, presupuesto | `require_director` en `dependencies.py` | test_auditoria A-01, O-2 |
| Ver qué pasa | monitor: constelación, relato, detalle | `monitor/index.html`, `flows.py`, `flows_repo.py` | test_flows_monitor, O-5, navegador |
| Arrancar / parar apps y fijar turnos | pestaña Aplicaciones | `launcher.py`, `config/apps.json` | test_launcher, E2E |
| Conectar apps sin pegar tokens | ficheros de conexión, credencial del Broker | `conexion.py`, `app._load_tokens`, `credentials.py` | test_conexion_credenciales, A-06, O-8 |
| Recuperarse de cortes | recibos que sólo avanzan, `/operations/status` | `restore_repo.py` | test_api_regressions_0_2_1, E2E |
| Arrancar Core con seguridad | `serve` (HTTP local + HTTPS en red) | `serve.py`, `run.bat`, `run_local.ps1` | test_serve_puerto, prueba A-12 |
| Probar sin tocar lo real | pytest / unittest | `tests/__init__.py` + primera línea de cada módulo | test_aislamiento_tests |

## 4. Registro por ID

Estados: VERIFICADO = cumple criterios con evidencia; BLOQUEADO = depende de una decisión del usuario.

| ID | Cat. | Descripción y origen | Evidencia inicial | Prio. | Implementación | Verificación | Estado |
|---|---|---|---|---|---|---|---|
| A-00 (+O-1, O-6) | defecto | `unittest discover -s tests` (y desde `tests/integration`, árbitro O-1; variables del usuario respetadas con `setdefault`, árbitro O-6) no aislaba: base real, carpeta de conexión y tokens del usuario | reproducido (incidente §7); árbitro: 15 ficheros en perfil falso | crítica | primera línea de cada `test_*.py` ejecuta `tests/__init__.py`; éste fija base y carpeta temporales y `AI_OS_AUTO_TOKENS=false` aunque el usuario los tenga (O-6); `run.bat`, `run_tests.ps1`, README con pytest | `test_aislamiento_tests` (3 carpetas, usuario con tokens/auto/base propia) muerde; unittest desde las 3 carpetas en perfil falso: OK y 0 ficheros | VERIFICADO |
| A-01 | defecto | Un token de app administraba: políticas, aprobaciones, servicios, capacidades, cuentas | sonda: 201 y DENY global efectivo | crítica | `require_director` (compartido con el lanzador) en esas rutas | tests A-01 muerden; E2E «app no crea DENY global» | VERIFICADO |
| O-2 | defecto (árbitro) | Una app gastaba el saldo de otra, agotaba sus aprobaciones, cambiaba sus metas; relaciones sin dueño | árbitro, ejecutado | alta | director en metas/objetivos (escrituras) y presupuesto; `approvals/use` sólo ámbito `<app>:`; relaciones sólo desde recurso propio. La decisión del planificador no guarda estado: abierta | 3 tests O-2 muerden; 2 tests antiguos adaptados (crear metas con token de app era el defecto) | VERIFICADO |
| A-02 | defecto | `policy_id` cambiaba de scope/key: 201 sin cambio | sonda | alta | 409 en `save_policy` | test muerde | VERIFICADO |
| A-03 | defecto | Revisión menor pisaba a la mayor | sonda | alta | 409 | test muerde | VERIFICADO |
| O-3 | defecto (árbitro) | Misma revisión con otra decisión → 200 | árbitro, ejecutado | media | misma revisión sólo cambia `enabled`; otro cambio → 409 | test muerde; sembrado ×2 y guiones (sólo `enabled`) siguen | VERIFICADO |
| A-04 | defecto | Gemelas `(policy_key, scope)` habilitadas | sonda | alta | 409 al guardar | test muerde | VERIFICADO |
| O-4 | riesgo (árbitro) | Gemelas ya existentes en una base anterior | lectura | media | aviso en el registro al arrancar; sin índice único (fallaría el arranque con datos viejos) | base real (copia): 0 gemelas, arranque sin avisos | VERIFICADO |
| A-05 | defecto | Recursos a nombre de otra app | sonda | alta | `owner_service` entre las afirmaciones del token | test muerde | VERIFICADO |
| A-06 | defecto | Releer tokens en marcha regeneraba ficheros con tokens rechazados | sonda: 401 | media | `app.state.tokens` leído una vez; monitor, lanzador y serve lo usan | test muerde | VERIFICADO |
| O-8 | defecto (árbitro) | `director=…` en `AI_OS_API_TOKENS` contaba como app | lectura | baja | se trata como director | test muerde | VERIFICADO |
| A-07 | defecto | Versión 0.4.4 tras anunciar 0.4.5 | lectura | media | 0.4.6 en `pyproject`/`__init__`, README con los cambios de 0.4.5 | `/health` 0.4.6; cabecera del monitor v0.4.6 | VERIFICADO |
| A-08 | defecto | Detalle del monitor incompleto | lectura | media | detalle desde `GET /flows/{id}` | navegador: página con 300 pasos, detalle con 350 | VERIFICADO |
| O-5 | defecto (árbitro) | `GET /flows/{id}` sin tope | lectura | media | `?limit=N` y `total`; el monitor pide 300 | test muerde; navegador «350 pasos: se ven los últimos 300» | VERIFICADO |
| A-15 | usabilidad | SVG enorme en flujos largos | base real (1 809 pasos) | baja | tope de 300 dibujados con aviso | navegador: 300 filas | VERIFICADO |
| O-7 | usabilidad (árbitro) | Fallo de red silencioso en el detalle; poda no avisada en `run.bat migrate` | lectura | baja | aviso «Core no contesta…»; echo en `run.bat`; manual | navegador con fetch caído: aviso visible | VERIFICADO |
| A-09 | defecto | Estado vacío con `:8000` | lectura | baja | `location.origin` | navegador con base vacía: URL real | VERIFICADO |
| A-10 | usabilidad | Pantalla de token sin decir dónde está el del director | lectura (heurística) | media | texto nuevo; ruta que no se sale del recuadro | navegador: captura; token de app → 403 claro al arrancar | VERIFICADO |
| A-11 | mejora | `flow_events` sin límite | datos reales | media | poda a 90 días (`AI_OS_MONITOR_RETENTION_DAYS`, 0 = nunca), al arrancar y cada hora; índice (migración 007) | test muerde; copia real: 75 861 conservados (todo < 90 días) | VERIFICADO |
| A-12 | defecto | `run_local.ps1` abría HTTP a la red | lectura + entorno | alta | usa `serve` | con `AI_OS_HOST=0.0.0.0` y sin certificado: se niega, nada escucha | VERIFICADO |
| A-13 | usabilidad | Flujos en memoria del navegador sin límite | lectura (heurística) | baja | tope de 1 000; cifras «de esta sesión» (title) | lectura del código; página estable con 450+ flujos | VERIFICADO |
| A-14 | usabilidad | Pestañas sin teclado | lectura | baja | flechas, Inicio, Fin; tabindex | navegador: teclas cambian pestaña y foco | VERIFICADO |
| A-16 | defecto | `run.bat docs` abría Swagger antes de tiempo | lectura | baja | `AI_OS_OPEN_MONITOR=docs` | `test_serve_puerto::AbrirDocumentacion`: abre `/docs` sólo tras 3 sondeos de `/health` (navegador sustituido) | VERIFICADO |
| A-17 | doc | `apps.json` pedía tocar `PRINCIPALS` | lectura | baja | comentario | JSON válido | VERIFICADO |
| A-19 | doc | Manual en 0.2.1 (puerto 8000, sin monitor ni tokens) | lectura | media | manual 0.4.6 + PDF | captura de la sección nueva; PDF regenerado | VERIFICADO |
| A-18 | datos reales | Restos de pruebas antiguas en la base real (metas «Meta Smoke Test», cuentas `acc_*`, políticas `scope_*`, servicio `127.0.0.1:9`) | base real | baja | autorizado el 19-nov: copia `ai_os_core.antes-borrar-restos-pruebas-20261119.db` y borrado de 19 metas, 6 planes, 20 auditorías, 6 cuentas, 6 reservas, 5 políticas (`scope_*`, `plan_scope_*`) y 4 servicios «n» del sondeo del 18-oct, con Core parado | quedan sólo las 18 políticas `<app>:broker`; `integrity_check` ok; Core arranca y las apps entran | VERIFICADO |

Descartes (con motivo): lectura de flujos con token de app (decisión documentada: sólo metadatos); transiciones de estado de metas (la especificación no las define; no se inventa regla); revocar una autorización inexistente ya daba 404 (falso positivo); icono 404 de apps sin icono (diseño: cae en `desconocida.svg`).

## 5. Pruebas ejecutadas

| ID | Objetivo | Comando / pasos | Resultado |
|---|---|---|---|
| P-1 | Suite | `python -m pytest -q` | PASA: 126 (7 subtests) |
| P-2 | Lint | `python -m ruff check .` | PASA |
| P-3 | Aislamiento | `unittest discover -s tests`, `-s tests/integration`, `-s tests/unit` con `LOCALAPPDATA` falso y `AI_OS_AUTO_TOKENS=true` | PASA: OK y 0 ficheros |
| P-4 | Tests muerden | deshacer cada arreglo en una copia (A-00, A-01, A-02..04, A-05, A-06, O-1, O-2, O-3, O-5, O-8) | PASA: cada test falla sin su arreglo |
| P-5 | E2E HTTP real | Core 0.4.6 (`serve`, 8796) sobre copia de la base real; sembrado ×2; `recorrido.py 1` | PASA: 21/21 |
| P-6 | Persistencia | reiniciar Core; `recorrido.py 2` | PASA: 4/4 (políticas y turno persisten; token del Broker sólo en memoria) |
| P-7 | Migración con datos reales | arrancar sobre copia real | PASA: esquema 7, 75 861 pasos conservados, sin gemelas |
| P-8 | Monitor | navegador headless: token por `#token`, detalle 350/300, offline, pantalla de token, token de app, pestañas, estado vacío | PASA |
| P-9 | Red | `run_local.ps1` con `AI_OS_HOST=0.0.0.0` sin certificado | PASA: se niega |
| P-10 | Apps reales contra Broker real (autorizado) | `verify_ai_os_core.py` de cada app contra un Core 0.4.6 de prueba (8796, base vacía + sembrado + token del Broker publicado como hace el runner) y el Broker real del PC IA, de una en una | PASA en las 7 apps con guion: Trading AI 6/6, Local AI Lab 7/7, Model_Drift 12/12, Knowledge Orchestrator 7/7, Athena 9/9, Agora 9/9, Gestión Tareas IA 11/11 (61 comprobaciones). Gestión Favoritos no tiene guion. Notas: KO y Agora se ejecutaron con una copia de su guion en el scratchpad por dos defectos de esos guiones (no de Core), ver §9; la primera pasada de GTI falló porque el modelo devolvió una subtarea que dependía de sí misma (validación de GTI, variación del modelo) y la segunda pasó. |
| P-11 | Core real tras reiniciar (autorizado) | parar el árbol de procesos, borrar restos, `Arrancar AI OS Core.bat` | PASA: `/health` 0.4.6, esquema 7, 8720 + 8443; los 11 ficheros de conexión (Athena y ChatyGPT con sus tokens nuevos) responden 200; el runner del PC IA vuelve a publicar el token del Broker por HTTPS |

Componentes reales: Core, SQLite, uvicorn, monitor en Chromium. Simulados: las apps (sus llamadas se reprodujeron por HTTP con sus tokens), el lanzamiento real de procesos (los tests lo sustituyen; E2E con catálogo de prueba).

## 6. Arbitraje

- Modalidad: agente independiente, sólo lectura, con las instrucciones, la especificación, el registro y las evidencias.
- Ronda 1: 8 objeciones (2 altas: O-1, O-2; 3 medias: O-3, O-4, O-5; 3 bajas: O-6, O-7, O-8). Todas aceptadas y corregidas (ver tabla). Sin objeción: rutas de gobierno de A-01, compatibilidad con apps y guiones, concurrencia de políticas, A-12/A-16.
- Ronda 2: las 8 objeciones comprobadas como resueltas ejecutando (pytest 126; unittest desde las 3 carpetas con 0 ficheros en el perfil; sonda de O-2, O-3, O-5 y O-8) y leyendo (O-4, O-7, guiones de Core y de las apps). Sin regresiones. Una objeción baja, R2-1 (este apartado remitía a una sección que no existía y O-1/O-6 no tenían fila), corregida.
- Nota del árbitro, no objeción: `approvals/use` con una autorización inexistente da 403 en vez de 404; ya era así antes (no regresión), se deja.
- Rondas realizadas: 2 de 3 posibles. Resultado: aprobado sin objeciones pendientes.

## 7. Incidente y reparación

- 13:37–13:38: dos ejecuciones de `unittest discover -s tests` escribieron en la base real (62 pasos, 11 políticas, 8 metas, 8 auditorías, 2 certificaciones, 4 paquetes, 2 planes, 14 claves; borraron el turno Urgente de Athena y 3 claves caducadas) y reescribieron `conexion\athena.json` y `conexion\chatygpt.json` con tokens de prueba, más 3 ficheros nuevos.
- Ningún proceso real se lanzó ni se cerró (lanzamiento y parada simulados en esos tests). Las políticas añadidas no cambiaron ninguna decisión real.
- Reparación: copia del estado dañado en `%LOCALAPPDATA%\AIOSCore\data\ai_os_core.antes-reparar-auditoria-20261119.db`; las 9 tablas afectadas restauradas fila a fila a la copia tomada antes (comprobado igual); ficheros basura borrados; `athena.json` y `chatygpt.json` con tokens nuevos fuertes.
- Core reiniciado el 19-nov con tu autorización: los dos tokens nuevos funcionan (P-11).

## 8. Puesta en marcha y estado final

- Hecho: Core real en 0.4.6 (P-11), restos de pruebas borrados (A-18).
- Si algún guion propio administra con token de app, cambiarlo al del director.
- **Estado: COMPLETADO Y VERIFICADO.** Todos los elementos del registro están en VERIFICADO; P-1 a P-11 pasan. El corte por falta de memoria del equipo (19-nov, tarde) se resolvió relanzando las verificaciones de una en una como procesos independientes.

## 9. Hallazgos fuera de Core

Aparecieron al ejecutar P-10. Son de los guiones de verificación de otras apps, no de Core ni de esas apps en producción. **Corregidos el 19-nov a petición del usuario** (ver al final).
- **Knowledge Orchestrator** `scripts/verify_ai_os_core.py`: usa siempre el id `verify_core_allow`, así que su clave de idempotencia (`verify_core_allow:1:single`) es la misma en todas las ejecuciones; el Broker la recuerda de una pasada anterior con otro contenido y responde 409. Arreglo: añadir un sufijo único por ejecución (como hace la copia `scratchpad/p10/verify_ko_unico.py`).
- **Agora** `scripts/verify_ai_os_core.py`: reenvía al Broker por `http://192.168.1.52:8765`, pero el Broker sólo sirve HTTPS desde el 20-oct. Arreglo: `https://127.0.0.1:8765` con transporte que confíe en `C:\Agora\pki-broker\ca.crt` (copia `scratchpad/p10/verify_agora_https.py`). El venv de Agora sigue sin dependencias (ya conocido); se usó uno en el scratchpad.

Corrección (19-nov, a petición del usuario):
- KO `scripts/verify_ai_os_core.py`: sufijo `RUN` (8 hex aleatorios) en los tres ids de captura. Prueba: dos ejecuciones seguidas contra el Broker real, 7/7 y 7/7, con claves `verify_core_allow_4cfe6acf:1:single` y `verify_core_allow_81a2e981:1:single` (antes la segunda daba 409).
- Agora `scripts/verify_ai_os_core.py`: `https://127.0.0.1:8765` y transporte que confía en `AI_BROKER_CA_CERT` (por defecto `C:\Agora\pki-broker\ca.crt`); con un transporte propio httpx ignora el `verify` del cliente. Prueba: 9/9 contra el Broker real con el guion del repo.
- ruff limpio en ambos; mypy de esos repos no cubre `scripts/`. Sin commits.
