from __future__ import annotations
import json, sys
from pathlib import Path
from collections import defaultdict, deque

ROOT = Path(__file__).resolve().parent
REG = json.loads((ROOT / "spec_registry.json").read_text(encoding="utf-8"))
errors, warnings = [], []

def err(code,msg): errors.append((code,msg))
def warn(code,msg): warnings.append((code,msg))

spec = REG["spec"]
if spec.get("source_of_truth") != "NORMATIVE_SPEC_0_4.md":
    err("SRC001","source_of_truth incorrecta")
if len(spec.get("precedence",[])) != len(set(spec.get("precedence",[]))):
    err("SRC002","precedence con duplicados")

contracts = REG["contracts"]
if len(contracts) != len(set(contracts)):
    err("CON001","contratos canónicos duplicados")
known_contracts = set(contracts)

phases = REG["phases"]
known_phases = set(phases)
reqs = {}
for r in REG["requirements"]:
    rid = r.get("id")
    if not rid: err("REQ000","requirement sin id"); continue
    if rid in reqs: err("REQ001",f"requirement duplicado: {rid}")
    reqs[rid] = r
    for field in ("owner","provider_phase","tests","contracts"):
        if not r.get(field): err("REQ002",f"{rid} sin {field}")
    if r.get("provider_phase") not in known_phases:
        err("REQ003",f"{rid}: provider_phase desconocida")
    for c in r.get("contracts",[]):
        if c not in known_contracts:
            err("REQ004",f"{rid}: contrato no registrado {c}")

for mid, m in REG["milestones"].items():
    for rid in m.get("requirements",[]):
        if rid not in reqs:
            err("MIL001",f"{mid}: requirement no registrado {rid}")

graph = {p:set(v.get("requires",[])) for p,v in phases.items()}
for p,deps in graph.items():
    for d in deps:
        if d not in graph: err("PHA001",f"{p}: dependencia desconocida {d}")
indeg={p:0 for p in graph}; adj=defaultdict(set)
for p,deps in graph.items():
    for d in deps: adj[d].add(p); indeg[p]+=1
q=deque([p for p,n in indeg.items() if n==0]); seen=[]
while q:
    x=q.popleft(); seen.append(x)
    for y in adj[x]:
        indeg[y]-=1
        if indeg[y]==0: q.append(y)
if len(seen)!=len(graph):
    err("PHA002","ciclo en dependencias")

known_cases=set(REG["critical_cases"])
for r in REG["requirements"]:
    for t in r.get("tests",[]):
        if t not in known_cases:
            err("TST001",f"{r['id']}: test/caso desconocido {t}")

if len(REG.get("pre_p01_artifacts",[])) < 9:
    err("DOC001","puerta pre-P01 incompleta")

unapproved=[d["id"] for d in REG["decisions"] if d.get("status")!="approved"]
if unapproved:
    warn("GATE001","Decisiones pendientes: "+", ".join(unapproved))

print("AI OS Core Spec Verifier 0.4")
print("="*34)
print("Errors:", len(errors))
for c,m in errors: print(f"ERROR {c}: {m}")
print("Warnings:", len(warnings))
for c,m in warnings: print(f"WARN  {c}: {m}")

if errors:
    print("\nRESULT: FAIL")
    sys.exit(1)
elif unapproved:
    print("\nRESULT: CONSISTENT_DRAFT")
    print("No generar prompts de implementación todavía.")
    sys.exit(0)
else:
    print("\nRESULT: APPROVED_FOR_PROMPT_DERIVATION")
