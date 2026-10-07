# Resolución de la revisión de Specification 0.5

| Hallazgo | Resolución 0.6 |
|---|---|
| S01 reglas de seguridad perdidas | Restituidas como invariantes obligatorios: default deny, classification ceiling, service endpoint/SSRF y credential redirect |
| S02 dependencias de aceptación | El verificador valida ID/revisión/hash exactos y dependencias transitivas; dependencia ausente, invalidada o circular invalida el consumidor |
| S03 decisiones anteriores sin destino | Añadida `PRESERVATION_MATRIX_0_4_TO_0_6.md` y anchors `INV-*` exigidos por el verificador |
| S04 garantías del verificador | Se prohíbe P10 como provider; se verifica precedencia provider→verifier; cobertura test↔requirement se comprueba en ambos sentidos |

## Aclaración

`covers` y `expected` demuestran trazabilidad declarada, no que el test pruebe semánticamente toda la función. Esa evaluación sigue siendo humana hasta que exista una prueba implementada y revisada.
