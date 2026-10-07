# Prompt 10 — E2E integrado sin Planner ni autonomía

## FASE ARQUITECTÓNICA
OS-5.

## PRERREQUISITOS
Prompts 01–08 relevantes aceptados.

## OBJETIVO
Demostrar valor con un flujo manual y auditable.

## FLUJO
1. ChatyGPT crea Goal.
2. Humano crea/acepta Objective.
3. Gestión Tareas crea Task.
4. Si IA: calcula schedule provisional/confirmed según reservation.
5. Crea Job en Agora con binding.
6. Agora reclama worker compatible.
7. Athena ejecuta.
8. Broker sirve modelo dentro del conjunto autorizado.
9. Registrar modelo efectivo/fallback.
10. Athena verifica.
11. Artifact versionado.
12. Agora finaliza Job.
13. Gestión Tareas agrega Jobs según política de Task.
14. Objective/Goal sólo avanzan tras criterios explícitos, no por simple Job completed.
15. UI muestra trazabilidad.

## CASOS OBLIGATORIOS
- duplicate create command concurrente;
- Core offline mientras productor genera eventos;
- delayed started después de completed;
- approval expira;
- model changes between precheck and inference;
- strict certification + Broker fallback attempt;
- context source changes after Run;
- multi-job mixed result;
- hybrid task human start/end;
- two GPU competitors;
- unauthorized service URL;
- service tries to publish another owner's event.

## EVIDENCIA
Guardar timeline, revisions, bindings, effective model, certification applicability, artifact hash y verification.
