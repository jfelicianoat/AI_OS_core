# AI OS Core — Control Plane (M0) · v0.2.0

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
