# Prompt 02 — Core: registry avanzado, proyecciones y Policy foundation

## FASE ARQUITECTÓNICA
OS-1 extendido.

## PRERREQUISITOS
Prompt 01 aceptado.

## ENTREGABLE EXCLUSIVO
Completar la infraestructura determinista que consumirán adaptadores externos, sin ejecutar trabajo de usuario.

## SERVICE/CAPABILITY
Separar:
- self health;
- connectivity;
- registration lifecycle.

CapabilityAvailability debe exponer:
- declared provider status;
- certification applicability;
- policy status;
- effective status;
- reasons.

## POLICY FOUNDATION
Implementar exactamente la semántica aprobada en 00C:
- TRUE/FALSE/UNKNOWN;
- constraints acumuladas;
- obligations;
- no ALLOW implícito por UNKNOWN.

## RECONCILIATION
- owner externo es autoridad;
- comparar `resource_revision`;
- no retroceder;
- conflicto same revision/different payload => audit + quarantine/manual investigation.

## CONTEXT
Sólo context local básico:
- Goal;
- Objective;
- Decision;
- Policy;
- Resource refs.
No consultar KO todavía.

## PRUEBAS
- policy approval + cost constraint conserva ambos;
- stale connectivity no equivale a unhealthy self;
- owner event delayed no revierte;
- unauthorized source event rejected;
- SSRF-like service URL rejected.
