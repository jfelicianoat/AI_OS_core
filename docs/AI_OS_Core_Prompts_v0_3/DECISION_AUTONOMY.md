# Decisión candidata — Autonomía
Estado: proposed

No calcular mínimo entre magnitudes heterogéneas.

Pipeline:
1. authorization gate
2. certification gate
3. admission gate
4. autonomy ceiling: mínimo sólo entre A0–A5
5. conservar por separado constraints/obligations/approval/cost/resource limits

EffectiveExecutionDecision:
- executable: bool
- blocked_reasons[]
- autonomy_ceiling: A0..A5 | null
- constraints
- obligations

executable=false no equivale a A0.
