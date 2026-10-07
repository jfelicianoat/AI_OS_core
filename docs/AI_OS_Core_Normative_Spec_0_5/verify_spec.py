from __future__ import annotations
import json, hashlib, sys
from pathlib import Path
from collections import defaultdict, deque

ROOT=Path(__file__).resolve().parent
reg=json.loads((ROOT/"spec_registry.json").read_text(encoding="utf-8"))
acc=json.loads((ROOT/"acceptance_registry.json").read_text(encoding="utf-8"))
tests=json.loads((ROOT/"test_catalog.json").read_text(encoding="utf-8"))
manifest=json.loads((ROOT/"manifest.json").read_text(encoding="utf-8"))

errors=[]
warnings=[]

def err(code,msg): errors.append((code,msg))
def warn(code,msg): warnings.append((code,msg))
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()

EXPECTED_SOURCE="NORMATIVE_SPEC_0_5.md"
EXPECTED_VERSION="0.5"
EXPECTED_PRECEDENCE=[
    "NORMATIVE_SPEC_0_5.md","formal_contracts_0.5",
    "accepted_acceptance_records","historical_docs"
]
EXPECTED_DECISIONS={"D-POLICY","D-APPROVAL","D-EVENT","D-SQLITE","D-SCHEDULING","D-AUTONOMY"}
EXPECTED_CONTRACTS={
    "ResourceReference","IdentityBinding","ResourceRevision","ProducerStreamIdentity",
    "Goal","Objective","CapabilityManifest","SkillManifest","CapabilityAvailability",
    "ModelIdentityEvidence","ExecutionFingerprint","ModelExecutionConstraint","ModelInvocationEvidence",
    "ComparabilityAssessment","EvaluationVerdict","Certification","CertificationApplicability","CertificationRequest",
    "Policy","PolicyDecision","PolicyObligation","ConstraintSet","ApprovalRequest","ApprovalAuthorization",
    "ApprovalUse","ApprovalRevocation","ApprovalEffectiveState","BudgetReservation",
    "EventEnvelope","CommandEnvelope","EventDeliveryReceipt","ReplayCursor","ReplayGap",
    "OperationStatusQuery","OperationExecutionStatus","OperationReceipt",
    "Task","HumanWorkSegment","TaskDependency","AICapacityForecast","WorkerAdmission","InferenceAdmission",
    "Job","JobDispatchRequest","AgentRun","Artifact","VerificationResult","Failure",
    "ContextRequest","ContextPackage","TypedPlanProposal","EffectiveExecutionDecision",
    "ServiceRegistration","ServiceHealth","AuthorizationPrincipal","DecisionTrace","AcceptanceRecord"
}
EXPECTED_PREP01={
    "DOC-CONTRACT-INVENTORY","DOC-DATA-DICTIONARY","DOC-STATE-TRANSITIONS",
    "DOC-AUTH-MATRIX","DOC-EVENT-AUTHORITY","DOC-PERSISTENCE-MAP",
    "DOC-CONTRACT-SCHEMAS","DOC-FIXTURES","DOC-ACCEPTANCE-BOOTSTRAP"
}
EXPECTED_M0={
    "M0-REGISTRY","M0-GOALS","M0-RESOURCE-GRAPH","M0-IDEMPOTENCY","M0-AUDIT",
    "M0-POLICY-BASE","M0-APPROVAL","M0-BUDGET","M0-CERT-PROJECTION",
    "M0-EVENTS","M0-RESTORE-FAKE"
}
EXPECTED_M2_MIN={
    "M2-APPROVAL","M2-BUDGET","M2-CERT","M2-MODEL-ENFORCEMENT",
    "M2-MODEL-EVIDENCE","M2-INFERENCE-ADMISSION","M2-JOB","M2-WORKER-ADMISSION",
    "M2-TASKJOB","M2-AGGREGATION","M2-HUMAN-SEGMENTS","M2-TRACE",
    "M2-REPLAY-BROKER","M2-REPLAY-ATHENA","M2-REPLAY-AGORA","M2-REPLAY-TASKS",
    "M2-RESTORE-BROKER","M2-RESTORE-AGORA"
}
EXPECTED_M2_CTX={"M2-CONTEXT-EVIDENCE","M2-REPLAY-KO"}

# 1. Manifest integrity and version
if manifest.get("version")!=EXPECTED_VERSION:
    err("MAN001","manifest version incorrecta")
for item in manifest.get("files",[]):
    path=ROOT/item["name"]
    if not path.exists():
        err("MAN002",f"archivo ausente: {item['name']}")
    elif sha(path)!=item["sha256"]:
        err("MAN003",f"hash no coincide: {item['name']}")

# 2. Source-of-truth binding
spec=reg.get("spec",{})
if spec.get("source_of_truth")!=EXPECTED_SOURCE:
    err("SRC001","source_of_truth incorrecta")
if spec.get("version")!=EXPECTED_VERSION:
    err("SRC002","spec registry version incorrecta")
if spec.get("precedence")!=EXPECTED_PRECEDENCE:
    err("SRC003","precedence no coincide con la norma 0.5")
src=ROOT/EXPECTED_SOURCE
if not src.exists():
    err("SRC004","fuente normativa ausente")
else:
    actual=sha(src)
    if spec.get("source_of_truth_sha256")!=actual:
        err("SRC005","spec_registry no está ligado al hash actual de la fuente normativa")

# 3. Mandatory decisions must exist exactly
mandatory=set(reg.get("mandatory_decisions",[]))
if mandatory!=EXPECTED_DECISIONS:
    err("DEC001",f"mandatory_decisions incorrectas: {sorted(mandatory)}")
decision_rows={d.get("id"):d for d in reg.get("decisions",[])}
if set(decision_rows)!=EXPECTED_DECISIONS:
    err("DEC002","lista de decisiones no coincide con las obligatorias")

# 4. Contracts unique
contracts=reg.get("contracts",[])
if len(contracts)!=len(set(contracts)):
    err("CON001","contratos duplicados")
known_contracts=set(contracts)
if known_contracts!=EXPECTED_CONTRACTS:
    err("CON002",f"catálogo contractual no coincide; missing={sorted(EXPECTED_CONTRACTS-known_contracts)} extra={sorted(known_contracts-EXPECTED_CONTRACTS)}")

# 5. Requirements
phases=reg.get("phases",{})
known_phases=set(phases)
req_rows={}
for r in reg.get("requirements",[]):
    rid=r.get("id")
    if not rid:
        err("REQ000","requirement sin id"); continue
    if rid in req_rows:
        err("REQ001",f"requirement duplicado {rid}")
    req_rows[rid]=r
    for fld in ("owners","provider_phases","verifier_phases","contracts","tests"):
        if not r.get(fld):
            err("REQ002",f"{rid} sin {fld}")
    for p in r.get("provider_phases",[])+r.get("verifier_phases",[]):
        if p not in known_phases:
            err("REQ003",f"{rid}: fase desconocida {p}")
    for c in r.get("contracts",[]):
        if c not in known_contracts:
            err("REQ004",f"{rid}: contrato no registrado {c}")

# 6. Exact milestone/profile coverage
profiles=reg.get("milestone_profiles",{})
m0=set(profiles.get("M0",{}).get("requirements",[]))
if m0!=EXPECTED_M0:
    err("MIL001",f"M0 coverage incorrecta; missing={sorted(EXPECTED_M0-m0)} extra={sorted(m0-EXPECTED_M0)}")
m2min=set(profiles.get("M2-minimal",{}).get("requirements",[]))
if m2min!=EXPECTED_M2_MIN:
    err("MIL002",f"M2-minimal coverage incorrecta; missing={sorted(EXPECTED_M2_MIN-m2min)} extra={sorted(m2min-EXPECTED_M2_MIN)}")
m2ctx=set(profiles.get("M2-contextual",{}).get("requirements",[]))
if m2ctx!=EXPECTED_M2_CTX or profiles.get("M2-contextual",{}).get("extends")!="M2-minimal":
    err("MIL003","M2-contextual incorrecto")
for rid in EXPECTED_M0|EXPECTED_M2_MIN|EXPECTED_M2_CTX:
    if rid not in req_rows:
        err("MIL004",f"requirement obligatorio no definido: {rid}")

# 7. Phase cycles
graph={p:set(v.get("requires",[])) for p,v in phases.items()}
for p,deps in graph.items():
    for d in deps:
        if d not in graph:
            err("PHA001",f"{p}: dependencia desconocida {d}")
indeg={p:0 for p in graph}; adj=defaultdict(set)
for p,deps in graph.items():
    for d in deps:
        adj[d].add(p); indeg[p]+=1
q=deque([p for p,n in indeg.items() if n==0]); seen=[]
while q:
    x=q.popleft(); seen.append(x)
    for y in adj[x]:
        indeg[y]-=1
        if indeg[y]==0: q.append(y)
if len(seen)!=len(graph):
    err("PHA002","ciclo en fases")

# 8. Test catalog must semantically claim each requirement it is assigned to
test_rows={t.get("id"):t for t in tests.get("tests",[])}
for rid,r in req_rows.items():
    for tid in r.get("tests",[]):
        t=test_rows.get(tid)
        if not t:
            err("TST001",f"{rid}: test inexistente {tid}")
        elif rid not in set(t.get("covers",[])):
            err("TST002",f"{tid} no declara cubrir {rid}")
for tid,t in test_rows.items():
    if not t.get("expected"):
        err("TST003",f"{tid} sin resultado esperado")
    if not t.get("covers"):
        err("TST004",f"{tid} no cubre ningún requirement")
    for rid in t.get("covers",[]):
        if rid not in req_rows:
            err("TST005",f"{tid}: requirement desconocido {rid}")

# 9. Pre-P01 identities exact, unique
prep=reg.get("pre_p01_artifacts",[])
prep_ids=[x.get("id") for x in prep]
if len(prep_ids)!=len(set(prep_ids)):
    err("DOC001","pre-P01 ids duplicados")
if set(prep_ids)!=EXPECTED_PREP01:
    err("DOC002","pre-P01 artifacts no coinciden con conjunto obligatorio")

# 10. Acceptance registry structural checks
acc_rows=acc.get("records",[])
by_artifact=defaultdict(list)
for a in acc_rows:
    by_artifact[(a.get("artifact_type"),a.get("artifact_id"))].append(a)

# Candidate consistency: accepted claims must be complete and aligned
spec_hash=spec.get("source_of_truth_sha256")
for d in EXPECTED_DECISIONS:
    row=decision_rows.get(d,{})
    recs=by_artifact.get(("decision",d),[])
    if len(recs)!=1:
        err("ACC001",f"{d}: debe existir exactamente un AcceptanceRecord de decisión")
        continue
    a=recs[0]
    if row.get("status")=="approved":
        required_ok=(
            a.get("status")=="accepted" and
            a.get("artifact_revision")==EXPECTED_VERSION and
            a.get("artifact_hash")==spec_hash and
            bool(a.get("accepted_by")) and bool(a.get("accepted_at")) and bool(a.get("evidence_refs"))
        )
        if not required_ok:
            err("ACC002",f"{d}: marcada approved sin AcceptanceRecord válido")
    if a.get("status")=="accepted" and row.get("status")!="approved":
        err("ACC003",f"{d}: AcceptanceRecord accepted pero decisión no approved")

# 11. Compute gates separately
candidate_consistent=(len(errors)==0)

def valid_decision_acceptance(d):
    row=decision_rows.get(d,{})
    recs=by_artifact.get(("decision",d),[])
    if len(recs)!=1: return False
    a=recs[0]
    return (
        row.get("status")=="approved" and a.get("status")=="accepted" and
        a.get("artifact_revision")==EXPECTED_VERSION and a.get("artifact_hash")==spec_hash and
        bool(a.get("accepted_by")) and bool(a.get("accepted_at")) and bool(a.get("evidence_refs"))
    )

spec_approved=candidate_consistent and all(valid_decision_acceptance(d) for d in EXPECTED_DECISIONS)

def valid_prep_artifact(aid):
    recs=by_artifact.get(("pre_p01_artifact",aid),[])
    if len(recs)!=1: return False
    a=recs[0]
    if a.get("status")!="accepted": return False
    if not all([a.get("artifact_revision"),a.get("artifact_hash"),a.get("accepted_by"),a.get("accepted_at"),a.get("evidence_refs"),a.get("artifact_path")]):
        return False
    path=ROOT/a["artifact_path"]
    if not path.exists(): return False
    return sha(path)==a["artifact_hash"]

pre_p01_ready=spec_approved and all(valid_prep_artifact(x) for x in EXPECTED_PREP01)

# warnings describe gates, not errors
if candidate_consistent and not spec_approved:
    warn("GATE001","Spec candidata consistente pero decisiones/aceptaciones no permiten SPEC_APPROVED")
if spec_approved and not pre_p01_ready:
    warn("GATE002","Spec aprobada pero puerta pre-P01 incompleta")

print("AI OS Core Spec Verifier 0.5")
print("="*34)
print(f"CandidateConsistency: {'PASS' if candidate_consistent else 'FAIL'}")
print(f"SpecApproved: {'YES' if spec_approved else 'NO'}")
print(f"PreP01Ready: {'YES' if pre_p01_ready else 'NO'}")
print(f"Errors: {len(errors)}")
for c,m in errors: print(f"ERROR {c}: {m}")
print(f"Warnings: {len(warnings)}")
for c,m in warnings: print(f"WARN  {c}: {m}")

if not candidate_consistent:
    print("\nRESULT: FAIL")
    sys.exit(1)
elif not spec_approved:
    print("\nRESULT: CONSISTENT_DRAFT")
    sys.exit(0)
elif not pre_p01_ready:
    print("\nRESULT: SPEC_APPROVED_NOT_PRE_P01_READY")
    sys.exit(0)
else:
    print("\nRESULT: PRE_P01_READY")
