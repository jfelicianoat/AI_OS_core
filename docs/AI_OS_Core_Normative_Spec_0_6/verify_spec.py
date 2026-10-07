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
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

EXPECTED_VERSION="0.6"
EXPECTED_SOURCE="NORMATIVE_SPEC_0_6.md"
EXPECTED_PRECEDENCE=[
 "NORMATIVE_SPEC_0_6.md","formal_contracts_0.6",
 "accepted_acceptance_records","historical_docs"
]
EXPECTED_DECISIONS={"D-POLICY","D-APPROVAL","D-EVENT","D-SQLITE","D-SCHEDULING","D-AUTONOMY"}
EXPECTED_INVARIANTS={
 "INV-SEC-DEFAULT-DENY","INV-SEC-CLASSIFICATION","INV-SEC-SERVICE-ENDPOINT",
 "INV-ID-LEGACY-BINDING","INV-APPROVAL-EXACT-SCOPED","INV-IDEMPOTENCY-ATOMIC",
 "INV-CONTEXT-VALIDITY","INV-TASK-DAG","INV-ARTIFACT-ROLES",
 "INV-PLANNER-BOUNDARY","INV-AUTONOMY-GATES"
}
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
 "M0-EVENTS","M0-RESTORE-FAKE","M0-AUTHORIZATION","M0-SERVICE-SECURITY",
 "M0-IDENTITY-REVISION"
}
EXPECTED_M2_MIN={
 "M2-APPROVAL","M2-BUDGET","M2-CERT","M2-MODEL-ENFORCEMENT","M2-MODEL-EVIDENCE",
 "M2-INFERENCE-ADMISSION","M2-JOB","M2-WORKER-ADMISSION","M2-TASKJOB",
 "M2-AGGREGATION","M2-HUMAN-SEGMENTS","M2-TRACE",
 "M2-REPLAY-BROKER","M2-REPLAY-ATHENA","M2-REPLAY-AGORA","M2-REPLAY-TASKS",
 "M2-RESTORE-BROKER","M2-RESTORE-AGORA","M2-TASK-DAG","M2-ARTIFACT-ROLES"
}
EXPECTED_M2_CTX={"M2-CONTEXT-EVIDENCE","M2-REPLAY-KO"}
VERIFICATION_ONLY={"P10-minimal","P10-contextual"}

# A. Manifest integrity
if manifest.get("version")!=EXPECTED_VERSION:
    err("MAN001","manifest version incorrecta")
for item in manifest.get("files",[]):
    path=ROOT/item.get("name","")
    if not path.exists():
        err("MAN002",f"archivo ausente: {item.get('name')}")
    elif sha(path)!=item.get("sha256"):
        err("MAN003",f"hash no coincide: {item.get('name')}")

# B. Source of truth
spec=reg.get("spec",{})
if spec.get("version")!=EXPECTED_VERSION: err("SRC001","spec version incorrecta")
if spec.get("source_of_truth")!=EXPECTED_SOURCE: err("SRC002","source_of_truth incorrecta")
if spec.get("precedence")!=EXPECTED_PRECEDENCE: err("SRC003","precedencia incorrecta")
src=ROOT/EXPECTED_SOURCE
if not src.exists():
    err("SRC004","fuente normativa ausente")
    source_text=""
    current_spec_hash=None
else:
    source_text=src.read_text(encoding="utf-8")
    current_spec_hash=sha(src)
    if spec.get("source_of_truth_sha256")!=current_spec_hash:
        err("SRC005","registry no está ligado al hash actual de la fuente normativa")

# C. Required decisions and invariants
mandatory=set(reg.get("mandatory_decisions",[]))
if mandatory!=EXPECTED_DECISIONS:
    err("DEC001","mandatory_decisions no coincide con el conjunto obligatorio")
decision_rows={d.get("id"):d for d in reg.get("decisions",[])}
if set(decision_rows)!=EXPECTED_DECISIONS:
    err("DEC002","decisions no coincide con el conjunto obligatorio")
for did,row in decision_rows.items():
    if row.get("artifact_revision")!=EXPECTED_VERSION or row.get("artifact_hash")!=current_spec_hash:
        err("DEC003",f"{did}: revisión/hash declarado no coincide con la fuente normativa 0.6")

mandatory_inv=set(reg.get("mandatory_invariants",[]))
if mandatory_inv!=EXPECTED_INVARIANTS:
    err("INV001","mandatory_invariants incompleto o alterado")
inv_rows={x.get("id"):x for x in reg.get("invariants",[])}
if set(inv_rows)!=EXPECTED_INVARIANTS:
    err("INV002","invariants no coincide con el conjunto obligatorio")
for iid,row in inv_rows.items():
    anchor=row.get("source_anchor")
    if not anchor or anchor not in source_text:
        err("INV003",f"{iid}: anchor normativo ausente de la fuente")
    if row.get("status")!="active":
        err("INV004",f"{iid}: invariant no activo sin decisión de sustitución")

# D. Contracts
contracts=reg.get("contracts",[])
if len(contracts)!=len(set(contracts)): err("CON001","contratos duplicados")
known_contracts=set(contracts)
if known_contracts!=EXPECTED_CONTRACTS:
    err("CON002",f"catálogo contractual divergente; missing={sorted(EXPECTED_CONTRACTS-known_contracts)} extra={sorted(known_contracts-EXPECTED_CONTRACTS)}")

# E. Requirements
phases=reg.get("phases",{})
known_phases=set(phases)
req_rows={}
for r in reg.get("requirements",[]):
    rid=r.get("id")
    if not rid:
        err("REQ000","requirement sin id"); continue
    if rid in req_rows: err("REQ001",f"requirement duplicado {rid}")
    req_rows[rid]=r
    for fld in ("owners","provider_phases","verifier_phases","contracts","tests"):
        if not r.get(fld): err("REQ002",f"{rid} sin {fld}")
    for p in r.get("provider_phases",[])+r.get("verifier_phases",[]):
        if p not in known_phases: err("REQ003",f"{rid}: fase desconocida {p}")
    for p in r.get("provider_phases",[]):
        if p in VERIFICATION_ONLY: err("REQ004",f"{rid}: fase verification-only usada como provider: {p}")
    for c in r.get("contracts",[]):
        if c not in known_contracts: err("REQ005",f"{rid}: contrato desconocido {c}")

# F. Exact milestone/profile coverage
profiles=reg.get("milestone_profiles",{})
m0=set(profiles.get("M0",{}).get("requirements",[]))
if m0!=EXPECTED_M0:
    err("MIL001",f"M0 divergente; missing={sorted(EXPECTED_M0-m0)} extra={sorted(m0-EXPECTED_M0)}")
m2=set(profiles.get("M2-minimal",{}).get("requirements",[]))
if m2!=EXPECTED_M2_MIN:
    err("MIL002",f"M2-minimal divergente; missing={sorted(EXPECTED_M2_MIN-m2)} extra={sorted(m2-EXPECTED_M2_MIN)}")
ctx=set(profiles.get("M2-contextual",{}).get("requirements",[]))
if ctx!=EXPECTED_M2_CTX or profiles.get("M2-contextual",{}).get("extends")!="M2-minimal":
    err("MIL003","M2-contextual divergente")
for rid in EXPECTED_M0|EXPECTED_M2_MIN|EXPECTED_M2_CTX:
    if rid not in req_rows: err("MIL004",f"requirement obligatorio no definido: {rid}")

# G. Phase DAG and provider-before-verifier
graph={p:set(v.get("requires",[])) for p,v in phases.items()}
for p,deps in graph.items():
    for d in deps:
        if d not in graph: err("PHA001",f"{p}: dependencia desconocida {d}")
indeg={p:0 for p in graph}; adj=defaultdict(set)
for p,deps in graph.items():
    for d in deps:
        adj[d].add(p); indeg[p]+=1
q=deque([p for p,n in indeg.items() if n==0]); seen=[]
while q:
    x=q.popleft(); seen.append(x)
    for y in adj[x]:
        indeg[y]-=1
        if indeg[y]==0:q.append(y)
if len(seen)!=len(graph): err("PHA002","ciclo en fases")

def precedes_or_same(a,b):
    if a==b:return True
    dq=deque([a]); visited={a}
    while dq:
        x=dq.popleft()
        for y in adj.get(x,()):
            if y==b:return True
            if y not in visited:
                visited.add(y); dq.append(y)
    return False

for rid,r in req_rows.items():
    for v in r.get("verifier_phases",[]):
        for p in r.get("provider_phases",[]):
            if p in graph and v in graph and not precedes_or_same(p,v):
                err("PHA003",f"{rid}: provider {p} no precede a verifier {v}")

# H. Test catalog, both directions
test_rows={t.get("id"):t for t in tests.get("tests",[])}
for rid,r in req_rows.items():
    for tid in r.get("tests",[]):
        t=test_rows.get(tid)
        if not t: err("TST001",f"{rid}: test inexistente {tid}")
        elif rid not in set(t.get("covers",[])):
            err("TST002",f"{rid}->{tid} no coincide con covers inverso")
for tid,t in test_rows.items():
    if not t.get("expected"): err("TST003",f"{tid} sin expected")
    if not t.get("covers"): err("TST004",f"{tid} sin covers")
    for rid in t.get("covers",[]):
        r=req_rows.get(rid)
        if not r: err("TST005",f"{tid}: requirement desconocido {rid}")
        elif tid not in set(r.get("tests",[])):
            err("TST006",f"{tid}->{rid} no coincide con lista tests del requirement")

# I. Pre-P01 identities and compatibility
prep=reg.get("pre_p01_artifacts",[])
prep_ids=[x.get("id") for x in prep]
if len(prep_ids)!=len(set(prep_ids)): err("DOC001","pre-P01 ids duplicados")
if set(prep_ids)!=EXPECTED_PREP01: err("DOC002","pre-P01 no coincide con conjunto obligatorio")
for x in prep:
    if x.get("compatible_spec_revision")!=EXPECTED_VERSION or x.get("compatible_spec_hash")!=current_spec_hash:
        err("DOC003",f"{x.get('id')}: compatibilidad declarada no coincide con spec 0.6")

# J. Acceptance registry: unique IDs, dependency graph, direct consistency
acc_rows=acc.get("records",[])
acc_by_id={}
acc_by_artifact=defaultdict(list)
for a in acc_rows:
    aid=a.get("acceptance_id")
    if not aid:
        err("ACC000","AcceptanceRecord sin acceptance_id"); continue
    if aid in acc_by_id: err("ACC001",f"acceptance_id duplicado {aid}")
    acc_by_id[aid]=a
    acc_by_artifact[(a.get("artifact_type"),a.get("artifact_id"))].append(a)

# dependency references and cycles
dep_graph={aid:set(a.get("depends_on",[])) for aid,a in acc_by_id.items()}
for aid,deps in dep_graph.items():
    for d in deps:
        if d not in acc_by_id: err("ACC002",f"{aid}: dependencia inexistente {d}")
state={}
def visit(aid,stack):
    st=state.get(aid)
    if st==1:
        err("ACC003",f"ciclo de aceptaciones: {' -> '.join(stack+[aid])}")
        return
    if st==2:return
    state[aid]=1
    for d in dep_graph.get(aid,()):
        if d in acc_by_id: visit(d,stack+[aid])
    state[aid]=2
for aid in acc_by_id: visit(aid,[])

def base_acceptance_complete(a):
    return (
      a.get("status")=="accepted" and bool(a.get("artifact_revision")) and bool(a.get("artifact_hash")) and
      a.get("compatible_spec_revision")==EXPECTED_VERSION and a.get("compatible_spec_hash")==current_spec_hash and
      bool(a.get("accepted_by")) and bool(a.get("accepted_at")) and bool(a.get("evidence_refs"))
    )

valid_cache={}
def acceptance_valid(aid,trail=None):
    if aid in valid_cache:return valid_cache[aid]
    a=acc_by_id.get(aid)
    if not a or not base_acceptance_complete(a):
        valid_cache[aid]=False; return False
    trail=set() if trail is None else set(trail)
    if aid in trail:
        valid_cache[aid]=False; return False
    trail.add(aid)
    for dep in a.get("depends_on",[]):
        if not acceptance_valid(dep,trail):
            valid_cache[aid]=False; return False
    # If a physical artifact_path is supplied, its hash must match.
    path=a.get("artifact_path")
    if path:
        fp=ROOT/path
        if not fp.exists() or sha(fp)!=a.get("artifact_hash"):
            valid_cache[aid]=False; return False
    valid_cache[aid]=True
    return True

# Any record claiming accepted but transitively invalid is an inconsistency.
for aid,a in acc_by_id.items():
    if a.get("status")=="accepted" and not acceptance_valid(aid):
        err("ACC004",f"{aid}: accepted pero no vigente/compatible transitivamente")

# Mandatory decisions: exact object/acceptance matching
for did in EXPECTED_DECISIONS:
    row=decision_rows.get(did,{})
    recs=acc_by_artifact.get(("decision",did),[])
    if len(recs)!=1:
        err("ACC005",f"{did}: requiere exactamente un AcceptanceRecord")
        continue
    a=recs[0]
    if a.get("artifact_revision")!=row.get("artifact_revision") or a.get("artifact_hash")!=row.get("artifact_hash"):
        err("ACC006",f"{did}: AcceptanceRecord no coincide con revisión/hash declarados por la decisión")
    if row.get("status")=="approved" and not acceptance_valid(a["acceptance_id"]):
        err("ACC007",f"{did}: approved sin aceptación vigente")
    if a.get("status")=="accepted" and row.get("status")!="approved":
        err("ACC008",f"{did}: aceptación accepted pero decisión no approved")

candidate_consistent=(len(errors)==0)

def valid_decision(did):
    row=decision_rows.get(did,{})
    recs=acc_by_artifact.get(("decision",did),[])
    return (
      row.get("status")=="approved" and len(recs)==1 and
      recs[0].get("artifact_revision")==row.get("artifact_revision") and
      recs[0].get("artifact_hash")==row.get("artifact_hash") and
      acceptance_valid(recs[0].get("acceptance_id"))
    )

spec_approved=candidate_consistent and all(valid_decision(d) for d in EXPECTED_DECISIONS)

def valid_prep(aid):
    recs=acc_by_artifact.get(("pre_p01_artifact",aid),[])
    if len(recs)!=1:return False
    a=recs[0]
    if not acceptance_valid(a.get("acceptance_id")):return False
    # Compatibility is checked independently of the artifact's own revision.
    return a.get("compatible_spec_revision")==EXPECTED_VERSION and a.get("compatible_spec_hash")==current_spec_hash and bool(a.get("artifact_path"))

pre_p01_ready=spec_approved and all(valid_prep(x) for x in EXPECTED_PREP01)

if candidate_consistent and not spec_approved:
    warn("GATE001","Candidata consistente; decisiones/aceptaciones aún no habilitan SPEC_APPROVED")
elif spec_approved and not pre_p01_ready:
    warn("GATE002","Spec aprobada; puerta documental pre-P01 todavía incompleta")

print("AI OS Core Spec Verifier 0.6")
print("="*34)
print(f"CandidateConsistency: {'PASS' if candidate_consistent else 'FAIL'}")
print(f"SpecApproved: {'YES' if spec_approved else 'NO'}")
print(f"PreP01Ready: {'YES' if pre_p01_ready else 'NO'}")
print(f"Errors: {len(errors)}")
for c,m in errors:print(f"ERROR {c}: {m}")
print(f"Warnings: {len(warnings)}")
for c,m in warnings:print(f"WARN  {c}: {m}")

if not candidate_consistent:
    print("\nRESULT: FAIL"); sys.exit(1)
elif not spec_approved:
    print("\nRESULT: CONSISTENT_DRAFT"); sys.exit(0)
elif not pre_p01_ready:
    print("\nRESULT: SPEC_APPROVED_NOT_PRE_P01_READY"); sys.exit(0)
else:
    print("\nRESULT: PRE_P01_READY"); sys.exit(0)
