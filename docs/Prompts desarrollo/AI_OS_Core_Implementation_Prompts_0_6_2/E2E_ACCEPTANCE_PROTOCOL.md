# Protocolo E2E

Cada requisito del perfil queda `SATISFIED`, `FAILED` o `NOT_VERIFIED`.
Un test negativo esperado cuenta como SATISFIED si demuestra el rechazo/bloqueo normativo.

## P10A / M2-minimal
PASS técnico sólo con 20/20 SATISFIED.
Cualquier FAILED → FAIL.
Cualquier NOT_VERIFIED indispensable → BLOCKED.
Un fallo correctamente atribuido no satisface el requisito.

## P10B / M2-contextual
Dos modos:
- `INHERIT_MINIMAL`: AcceptanceRecord M2-minimal vigente y compatible con contratos/builds/configuración/model constraints.
- `FULL_22`: comprobar directamente 22/22.

PASS técnico sólo con 22/22 SATISFIED por evidencia propia o heredada válidamente.
Cambios incompatibles invalidan evidencia heredada.

Approval/budget pueden no activarse en una operación concreta, pero siguen siendo requisitos: incluir escenarios que los activen cuando corresponda.
