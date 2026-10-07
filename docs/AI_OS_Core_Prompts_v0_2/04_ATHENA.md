# Prompt 04 — Athena: manifests, fingerprints y modelo efectivo

## FASE ARQUITECTÓNICA
OS-2.

## OBJETIVO
Integrar Athena sin cambiar su autoridad local de permisos.

## CAMBIOS
- Capability manifests de capacidades reales.
- Skill manifests con version/hash/toolsets.
- AgentRun status enum alineado al contrato.
- Execution evidence con model invocation refs.
- Context package snapshot/reference verificable.
- correlation IDs.

## MODELO EFECTIVO
Cada inferencia debe registrar:
- requested model/profile;
- allowed candidate set si existe;
- effective model servido;
- fallback flag/reason;
- model identity evidence observable.

Si un Job exige certificación estricta:
- Athena/Broker request debe impedir fallback fuera del set certificado;
- si el proveedor no garantiza eso, fallar antes de ejecutar como `CERTIFICATION_ENFORCEMENT_UNAVAILABLE`.

## APPROVALS
No aceptar un ApprovalGrant del Core como ampliación de permisos.
Si se implementa reconocimiento:
- validar principal/trust;
- action digest;
- expiry;
- resource revision;
- y volver a pasar PermissionEngine local.

## STANDALONE
Athena debe seguir funcionando sin Core cuando el run no declare integración/certification requirement.

## PRUEBAS
- explicit model no fallback;
- fallback registrado cuando permitido;
- strict certified run bloquea fallback no autorizado;
- ContextPackage no aumenta tool registry;
- late Core unavailable no convierte requisito obligatorio en permiso.
