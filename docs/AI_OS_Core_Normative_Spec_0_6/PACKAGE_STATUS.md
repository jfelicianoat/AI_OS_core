# Package Status — 0.6

- CandidateConsistency: PASS
- SpecApproved: NO
- PreP01Ready: NO
- Resultado esperado: `CONSISTENT_DRAFT`

Las seis decisiones normativas permanecen `proposed`.
No se han fabricado aprobaciones humanas ni artefactos pre-P01.

## Autocomprobaciones adversariales

El paquete incluye `test_verifier.py`, que prueba entre otros:
- flags de aprobación sin AcceptanceRecord;
- decisión ausente;
- M0 vacío;
- artefactos pre-P01 falsos;
- precedencia invertida;
- contrato obligatorio eliminado;
- aceptación directa invalidada;
- dependencia transitiva invalidada;
- revisión/hash de decisión discordantes;
- dependencia inexistente;
- ciclo de dependencias de aceptación;
- P10 usado como provider;
- verifier sin dependencia del provider;
- relación Test↔Requirement rota;
- eliminación de un invariant anchor obligatorio;
- cadena de dependencias válida;
- ruta positiva PRE_P01 simulada.

Estas pruebas son documentales y sintéticas. No equivalen a integración del producto.
