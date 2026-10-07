# Prompt 00F — Mapa físico, integraciones reales y MVP

## FASE ARQUITECTÓNICA
OS-0/OS-1 planning.

## OBJETIVO REAL
Asegurar que el primer producto resuelve un problema concreto sin sobrediseño.

## MAPA FÍSICO
Documentar proceso + máquina:
- AI OS Core: PC principal.
- Agora Board/API: PC principal.
- Agora Runner: PC IA.
- AI Broker servidor real: PC IA, tras identificar repositorio.
- Model Drift: ubicar explícitamente.
- KO / Gestión Tareas / ChatyGPT: PC principal salvo evidencia distinta.
- Athena: donde esté el workspace.

Para cada enlace:
- protocolo;
- dirección autorizada;
- autenticación;
- productor/relay;
- replay.

## SEGURIDAD DE ENDPOINTS
ServiceRegistration no permite arbitrary URL.
Crear allowlist por service identity:
- host/IP/CIDR permitido;
- puerto;
- `https` cuando cruce máquina;
- redirect policy;
- timeout;
- max response size;
- no forwarding de credential a redirecciones/destino diferente.

## MVP: 3 RECORRIDOS
Limitar primer Core a:
1. Registrar/observar servicios y capabilities.
2. Crear Goal/Decision y relacionarlos con recursos.
3. Ver trazabilidad de un flujo manual Task→Job→Run→Artifact.

Diferir:
- Planner;
- autonomía;
- semantic Context;
- automatic certification dispatch;
- complex approval delegation.

## MÉTRICAS A ACORDAR
No inventar resultados. Proponer targets:
- latencia API;
- event backlog;
- recovery time;
- max services/capabilities;
- freshness de health;
- RPO/RTO.

## CRITERIO DE CIERRE
Si estos tres recorridos requieren menos módulos/tablas que OS-1 previo, reducir alcance.
