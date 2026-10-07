# Changelog v0.3

Este changelog distingue **decisiones incorporadas al paquete** de **trabajo aún no ejecutado**.

## Decisiones candidatas ya escritas
- combinación de Policies por significado, no AND genérico;
- SQLite WAL + FULL para la DB transaccional inicial;
- ApprovalAuthorization inmutable y consumo/revocación separados;
- múltiples eventos legítimos por resource revision;
- stream epoch/sequence y replay-gap;
- prerequisitos E2E asignados a prompts concretos;
- nombres canónicos de contratos;
- gates de autorización/certificación/admisión separados de A0–A5;
- Planner propiedad de AI OS Core PlanningService, Task creation propiedad de Gestión Tareas.

## Trabajo todavía pendiente
- ejecutar P00 sobre docs históricos;
- materializar JSON Schemas/Pydantic/fixtures reales;
- localizar el repo servidor real de AI Broker;
- implementar P01+;
- ejecutar tests reales;
- aprobar o modificar humanamente las decisiones `proposed`.

Por tanto v0.3 no afirma que OS-0 esté cerrado ni que la implementación esté lista.
