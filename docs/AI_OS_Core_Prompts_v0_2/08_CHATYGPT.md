# Prompt 08 — ChatyGPT: UI del control plane con autorización correcta

## FASE ARQUITECTÓNICA
OS-3.

## OBJETIVO
Dar interfaz a Goals, trazabilidad y approvals sin convertir UI en barrera de seguridad.

## AI OS CLIENT
Consumir contratos versionados `0.2`.
Negociar features; no asumir endpoints futuros.

## APPROVAL INBOX
Mostrar:
- acción exacta;
- digest/version;
- recursos y revisión;
- policy;
- expiry;
- alcance;
- consecuencias;
- identidad autorizada.

El servidor valida; UI no es autoridad.

## CONTEXT EXPLANATION
Mostrar exclusiones según permisos:
- usuario sin permiso de existencia recibe razón genérica;
- auditor autorizado puede ver ref exacta.

## TRAZABILIDAD
Goal→Objective→Task→Job→Run→Artifact, distinguiendo:
- estado del owner;
- estado derivado/proyección;
- freshness.

## DEGRADACIÓN
Core apagado no rompe chat normal.

## PRUEBAS
- approval expira mientras pantalla abierta;
- acción muta tras aprobación => grant inválido;
- user sin scope no ve recurso excluido;
- stale projection se etiqueta.
