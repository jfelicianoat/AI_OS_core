# AI OS Core — Control Plane (M0) · v0.2.1

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
- Certificaciones de modelos del Broker (`proveedor/despliegue/modelo`): la consulta `GET /certifications/{model_id}/{capability_id}/{version}` admite barras en `model_id` (antes daba 404 y la certificación era ilegible).

### Pruebas con el resto de apps
Ninguna app llama todavía a Core; los dos recorridos lo ponen a dirigirlas de verdad (ambos verdes el 18-oct con el token activo):
- `scripts/e2e_broker_agora.py` (31): tarea LLM real en el Broker y proyección del tablero de Agora.
- `scripts/e2e_ecosistema.py` (33): certificaciones a partir de los resultados reales de Model_Drift, elección del modelo de Athena según esas certificaciones (`muse-glimmer:latest` autorizado; `qwen3.8:27b` y `lfm2:24b` descartados), run real de Athena sobre el Broker gobernado por Core, y proyección de las 76 tareas de una copia de Gestión Tareas IA con su estado canónico idéntico al origen.
- `scripts/e2e_resto_apps.py <core> <carpeta_copias>` (18): copias de las bases de ChatyGPT, Knowledge Orchestrator, Trading AI desktop y Local AI Lab. Core recomienda la acción correcta tras una caída para las 4 293 tareas al Broker de ChatyGPT y las 235 de KO (incluidas las que siguen en cola o en curso), y proyecta sus conversaciones, flujos, 11 backtests y 10 registros de experimentos con el estado canónico idéntico al origen. Verde también con Core arrancado sólo con tokens por app.
- LARM no entra en ningún recorrido: hoy sólo es especificación y prompts, no hay programa que gobernar.

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
