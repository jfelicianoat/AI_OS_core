# Casos críticos con resultado esperado

C01 Duplicate concurrent:
mismo principal+operation+key+body => una operación y mismo resultado lógico.
Misma key con body distinto => 409.

C02 Late event:
completed rev8 seguido de started rev7 => projection permanece completed rev8.

C03 Same revision:
delta completed + audit event rev8 => ambos válidos.
Dos full_state rev8 con state_digest distinto => contradiction/quarantine.

C04 Core offline:
productor acumula outbox y replay al volver Core.

C05 Replay gap:
seq faltante fuera de retención => REPLAY_GAP + snapshot/reconcile.

C06 Approval expiry:
expira antes de uso => ejecución rechazada, no ApprovalUse.

C07 Scoped approval:
max_uses=2, dos operation_id distintos consumen dos usos; tercero falla; retry del segundo no consume extra.

C08 Policy obligation:
requires_approval true + false => obligación de aprobación permanece.

C09 Budget concurrency:
dos reservas 80 sobre 100 => sólo una obtiene reserva completa.

C10 Model fallback:
allowed set {A,B}, intento C => bloquear/fallar antes de aceptar C.

C11 Identity enrichment:
unavailable→verified no implica automáticamente model changed.

C12 Historical context:
KO cambia fuente; Run antiguo recupera revisión/snapshot exacto.

C13 Multi-job:
all_required con 2 success + 1 fail => Task no completed.

C14 Hybrid:
5m inicio + IA +15m review => agenda bloquea segmentos, no wall clock.

C15 Restore:
receptor ya ejecutó operation X => consultar receipt, no duplicar.
