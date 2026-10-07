# Resolución de la revisión de Specification 0.6 — parche 0.6.1

## T01 — Referencias de versión

Corregido:
- la precedencia escrita apunta a `NORMATIVE_SPEC_0_6_1.md`;
- contratos formales se identifican como 0.6.1;
- el histórico incluye v0.5 y v0.6;
- `DOC-CONTRACT-SCHEMAS` se denomina `Contract Schemas 0.6.1`;
- registro, manifest y verificador apuntan a la misma fuente actual.

Prevención:
- `SRC006` compara la precedencia escrita del Markdown con la lista textual normativa esperada;
- `SRC007` detecta referencias directas obsoletas a fuentes normativas anteriores;
- `DOC004` valida el nombre exacto del artefacto pre-P01.

## T02 — Listas M0/M2

Corregido:
- M0 enumera exactamente 14 requisitos;
- M2-minimal enumera exactamente 20;
- M2-contextual hereda esos 20 y añade exactamente 2.

Los antiguos grupos conceptuales de replay/restore ya no sustituyen los IDs normativos expandidos.

Prevención:
- `MIL005` compara Markdown M0 con el conjunto normativo;
- `MIL006` compara Markdown M2-minimal;
- `MIL007` compara Markdown M2-contextual.

## Alcance

No se han cambiado:
- ownership;
- contratos funcionales;
- Policy semantics;
- approval semantics;
- eventos/replay;
- restore;
- certificación;
- scheduling;
- Planner boundary;
- autonomía.

Este parche es documental y de verificación.
