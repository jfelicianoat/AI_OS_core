# Decisión candidata — SQLite
Estado: proposed

El MVP usa una única DB SQLite para estado transaccional:
- WAL
- synchronous=FULL
- foreign_keys=ON
- busy_timeout
- transacciones cortas

No existe perfil por tabla.

Motivo: Goals/eventos/idempotencia/proyecciones pueden participar en la misma transacción.

No afirmar más durabilidad que la respaldada por SQLite + filesystem/hardware real.

Backup: SQLite Backup API.

Tras restore:
- `reconciliation_required`
- no replay de efectos externos a ciegas
- consultar receipt/operation_id del receptor si existe
- si no puede saberse, `manual_reconciliation_required`
