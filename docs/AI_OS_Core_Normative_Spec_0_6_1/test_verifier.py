from __future__ import annotations
import json, hashlib, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def load(root,name): return json.loads((root/name).read_text(encoding="utf-8"))
def save(root,name,obj):
    (root/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False),encoding="utf-8")

def update_manifest(root,*names):
    m=load(root,"manifest.json")
    rows={x["name"]:x for x in m["files"]}
    for name in names:
        if name in rows:
            rows[name]["sha256"]=sha(root/name)
    save(root,"manifest.json",m)

def run_variant(name,mutate,expected,expected_code=None):
    with tempfile.TemporaryDirectory() as td:
        dst=Path(td)/"pkg"
        shutil.copytree(SRC,dst,ignore=shutil.ignore_patterns("VERIFIER_OUTPUT.txt","SELFTEST_OUTPUT.txt","PACKAGE_STATUS.md"))
        mutate(dst)
        p=subprocess.run([sys.executable,"-S",str(dst/"verify_spec.py")],capture_output=True,text=True,cwd=dst)
        out=p.stdout+p.stderr
        ok=(expected in out) and (expected_code is None or expected_code in out)
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(out)
            raise SystemExit(1)

def noop(root): pass

def approve_flags_only(root):
    r=load(root,"spec_registry.json")
    for d in r["decisions"]: d["status"]="approved"
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def empty_decisions(root):
    r=load(root,"spec_registry.json"); r["decisions"]=[]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def empty_m0(root):
    r=load(root,"spec_registry.json"); r["milestone_profiles"]["M0"]["requirements"]=[]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def fake_prep(root):
    r=load(root,"spec_registry.json")
    r["pre_p01_artifacts"]=[{"id":f"FAKE-{i}","name":"x","compatible_spec_revision":"0.6.1","compatible_spec_hash":r["spec"]["source_of_truth_sha256"]} for i in range(9)]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def inverted_precedence(root):
    r=load(root,"spec_registry.json"); r["spec"]["precedence"]=list(reversed(r["spec"]["precedence"]))
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def missing_acceptance_contract(root):
    r=load(root,"spec_registry.json"); r["contracts"].remove("AcceptanceRecord")
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def proper_spec_approval(root):
    r=load(root,"spec_registry.json"); a=load(root,"acceptance_registry.json")
    for d in r["decisions"]: d["status"]="approved"
    for rec in a["records"]:
        if rec["artifact_type"]=="decision":
            rec["status"]="accepted"; rec["accepted_by"]="human-reviewer"
            rec["accepted_at"]="2026-09-12T17:00:00+01:00"; rec["evidence_refs"]=["review://spec-0.6.1"]
    save(root,"spec_registry.json",r); save(root,"acceptance_registry.json",a)
    update_manifest(root,"spec_registry.json","acceptance_registry.json")

def invalidated_direct(root):
    proper_spec_approval(root)
    a=load(root,"acceptance_registry.json")
    next(x for x in a["records"] if x["artifact_id"]=="D-POLICY")["status"]="invalidated"
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def proper_pre_p01(root):
    proper_spec_approval(root)
    r=load(root,"spec_registry.json"); a=load(root,"acceptance_registry.json")
    names={x["id"]:x["name"] for x in r["pre_p01_artifacts"]}
    for rec in a["records"]:
        if rec["artifact_type"]=="pre_p01_artifact":
            fp=root/"pre_p01"/f"{rec['artifact_id']}.md"; fp.parent.mkdir(parents=True,exist_ok=True)
            fp.write_text(f"# {names[rec['artifact_id']]}\\n\\nselftest artifact\\n",encoding="utf-8")
            rec.update({
              "artifact_revision":"test-r1","artifact_hash":sha(fp),"artifact_path":str(fp.relative_to(root)),
              "status":"accepted","accepted_by":"human-reviewer","accepted_at":"2026-09-12T17:05:00+01:00",
              "evidence_refs":["review://pre-p01-0.6.1"]
            })
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def decision_dep_invalidated(root):
    proper_spec_approval(root)
    a=load(root,"acceptance_registry.json"); r=load(root,"spec_registry.json")
    a["records"].append({
      "acceptance_id":"ACC-CONTRACT-X","artifact_type":"contract","artifact_id":"CONTRACT-X",
      "artifact_revision":"r1","artifact_hash":"a"*64,
      "compatible_spec_revision":"0.6.1","compatible_spec_hash":r["spec"]["source_of_truth_sha256"],
      "status":"invalidated","accepted_by":"reviewer","accepted_at":"2026-09-12T17:00:00+01:00",
      "evidence_refs":["review://x"],"depends_on":[],"invalidates_if_changed":[]
    })
    next(x for x in a["records"] if x["artifact_id"]=="D-POLICY")["depends_on"]=["ACC-CONTRACT-X"]
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def decision_revision_mismatch(root):
    proper_spec_approval(root)
    r=load(root,"spec_registry.json")
    d=next(x for x in r["decisions"] if x["id"]=="D-POLICY")
    d["artifact_revision"]="0.4"; d["artifact_hash"]="b"*64
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def prep_dep_invalidated(root):
    proper_pre_p01(root)
    a=load(root,"acceptance_registry.json"); r=load(root,"spec_registry.json")
    a["records"].append({
      "acceptance_id":"ACC-CONTRACT-Y","artifact_type":"contract","artifact_id":"CONTRACT-Y",
      "artifact_revision":"r1","artifact_hash":"c"*64,
      "compatible_spec_revision":"0.6.1","compatible_spec_hash":r["spec"]["source_of_truth_sha256"],
      "status":"invalidated","accepted_by":"reviewer","accepted_at":"2026-09-12T17:00:00+01:00",
      "evidence_refs":["review://y"],"depends_on":[],"invalidates_if_changed":[]
    })
    next(x for x in a["records"] if x["artifact_id"]=="DOC-FIXTURES")["depends_on"]=["ACC-CONTRACT-Y"]
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def missing_dependency(root):
    a=load(root,"acceptance_registry.json")
    next(x for x in a["records"] if x["artifact_id"]=="D-POLICY")["depends_on"]=["ACC-DOES-NOT-EXIST"]
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def dependency_cycle(root):
    a=load(root,"acceptance_registry.json")
    p=next(x for x in a["records"] if x["artifact_id"]=="D-POLICY")
    q=next(x for x in a["records"] if x["artifact_id"]=="D-APPROVAL")
    p["depends_on"]=[q["acceptance_id"]]; q["depends_on"]=[p["acceptance_id"]]
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")

def p10_as_provider(root):
    r=load(root,"spec_registry.json")
    next(x for x in r["requirements"] if x["id"]=="M2-JOB")["provider_phases"]=["P10-minimal"]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def remove_p10_dependencies(root):
    r=load(root,"spec_registry.json"); r["phases"]["P10-minimal"]["requires"]=[]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def break_reverse_test_link(root):
    r=load(root,"spec_registry.json")
    x=next(x for x in r["requirements"] if x["id"]=="M0-POLICY-BASE")
    x["tests"]=[t for t in x["tests"] if t!="C20"]
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")

def remove_invariant_anchor(root):
    s=root/"NORMATIVE_SPEC_0_6_1.md"
    txt=s.read_text(encoding="utf-8").replace("INV-SEC-DEFAULT-DENY","INV-REMOVED-ANCHOR")
    s.write_text(txt,encoding="utf-8")
    r=load(root,"spec_registry.json"); r["spec"]["source_of_truth_sha256"]=sha(s)
    for d in r["decisions"]: d["artifact_hash"]=sha(s)
    for x in r["pre_p01_artifacts"]: x["compatible_spec_hash"]=sha(s)
    save(root,"spec_registry.json",r)
    # Keep acceptance records compatible with source so the invariant check is isolated.
    a=load(root,"acceptance_registry.json")
    for rec in a["records"]: rec["compatible_spec_hash"]=sha(s)
    for rec in a["records"]:
        if rec["artifact_type"]=="decision": rec["artifact_hash"]=sha(s)
    save(root,"acceptance_registry.json",a)
    update_manifest(root,"NORMATIVE_SPEC_0_6_1.md","spec_registry.json","acceptance_registry.json")

def valid_dependency_chain(root):
    proper_spec_approval(root)
    a=load(root,"acceptance_registry.json"); r=load(root,"spec_registry.json")
    a["records"].append({
      "acceptance_id":"ACC-CONTRACT-VALID","artifact_type":"contract","artifact_id":"CONTRACT-VALID",
      "artifact_revision":"r1","artifact_hash":"d"*64,
      "compatible_spec_revision":"0.6.1","compatible_spec_hash":r["spec"]["source_of_truth_sha256"],
      "status":"accepted","accepted_by":"reviewer","accepted_at":"2026-09-12T17:00:00+01:00",
      "evidence_refs":["review://valid"],"depends_on":[],"invalidates_if_changed":[]
    })
    next(x for x in a["records"] if x["artifact_id"]=="D-POLICY")["depends_on"]=["ACC-CONTRACT-VALID"]
    save(root,"acceptance_registry.json",a); update_manifest(root,"acceptance_registry.json")


def retarget_source_hash(root):
    spec=root/"NORMATIVE_SPEC_0_6_1.md"
    h=sha(spec)
    r=load(root,"spec_registry.json")
    r["spec"]["source_of_truth_sha256"]=h
    for d in r["decisions"]: d["artifact_hash"]=h
    for x in r["pre_p01_artifacts"]: x["compatible_spec_hash"]=h
    save(root,"spec_registry.json",r)
    a=load(root,"acceptance_registry.json")
    for rec in a["records"]:
        rec["compatible_spec_hash"]=h
        if rec["artifact_type"]=="decision": rec["artifact_hash"]=h
    save(root,"acceptance_registry.json",a)
    update_manifest(root,"NORMATIVE_SPEC_0_6_1.md","spec_registry.json","acceptance_registry.json")

def markdown_wrong_precedence(root):
    p=root/"NORMATIVE_SPEC_0_6_1.md"
    t=p.read_text(encoding="utf-8").replace("1. `NORMATIVE_SPEC_0_6_1.md`","1. `NORMATIVE_SPEC_0_5.md`",1)
    p.write_text(t,encoding="utf-8")
    retarget_source_hash(root)

def markdown_missing_m0_requirement(root):
    p=root/"NORMATIVE_SPEC_0_6_1.md"
    t=p.read_text(encoding="utf-8").replace("- M0-AUTHORIZATION\n","",1)
    p.write_text(t,encoding="utf-8")
    retarget_source_hash(root)


def markdown_missing_m2_requirement(root):
    p=root/"NORMATIVE_SPEC_0_6_1.md"
    t=p.read_text(encoding="utf-8").replace("- M2-TASK-DAG\n","",1)
    p.write_text(t,encoding="utf-8")
    retarget_source_hash(root)

def wrong_contract_schemas_name(root):
    r=load(root,"spec_registry.json")
    next(x for x in r["pre_p01_artifacts"] if x["id"]=="DOC-CONTRACT-SCHEMAS")["name"]="Contract Schemas 0.5"
    save(root,"spec_registry.json",r); update_manifest(root,"spec_registry.json")


run_variant("base",noop,"RESULT: CONSISTENT_DRAFT")
run_variant("approve-flags-only",approve_flags_only,"RESULT: FAIL")
run_variant("empty-decisions",empty_decisions,"RESULT: FAIL")
run_variant("empty-M0",empty_m0,"RESULT: FAIL")
run_variant("fake-preP01",fake_prep,"RESULT: FAIL")
run_variant("inverted-precedence",inverted_precedence,"RESULT: FAIL")
run_variant("missing-AcceptanceRecord-contract",missing_acceptance_contract,"RESULT: FAIL")
run_variant("proper-spec-approval",proper_spec_approval,"RESULT: SPEC_APPROVED_NOT_PRE_P01_READY")
run_variant("invalidated-direct",invalidated_direct,"RESULT: FAIL")
run_variant("proper-preP01",proper_pre_p01,"RESULT: PRE_P01_READY")
run_variant("decision-dependency-invalidated",decision_dep_invalidated,"RESULT: FAIL")
run_variant("decision-revision-mismatch",decision_revision_mismatch,"RESULT: FAIL")
run_variant("preP01-dependency-invalidated",prep_dep_invalidated,"RESULT: FAIL")
run_variant("missing-acceptance-dependency",missing_dependency,"RESULT: FAIL")
run_variant("acceptance-dependency-cycle",dependency_cycle,"RESULT: FAIL")
run_variant("P10-as-provider",p10_as_provider,"RESULT: FAIL")
run_variant("P10-without-dependencies",remove_p10_dependencies,"RESULT: FAIL")
run_variant("reverse-test-link-broken",break_reverse_test_link,"RESULT: FAIL")
run_variant("mandatory-invariant-anchor-removed",remove_invariant_anchor,"RESULT: FAIL")
run_variant("valid-dependency-chain",valid_dependency_chain,"RESULT: SPEC_APPROVED_NOT_PRE_P01_READY")
run_variant("markdown-wrong-precedence",markdown_wrong_precedence,"RESULT: FAIL","SRC006")
run_variant("markdown-missing-M0-requirement",markdown_missing_m0_requirement,"RESULT: FAIL","MIL005")
run_variant("markdown-missing-M2-requirement",markdown_missing_m2_requirement,"RESULT: FAIL","MIL006")
run_variant("wrong-contract-schemas-name",wrong_contract_schemas_name,"RESULT: FAIL","DOC004")
print("ALL SELFTESTS PASS")
