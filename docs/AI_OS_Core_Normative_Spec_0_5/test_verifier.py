from __future__ import annotations
import json, hashlib, shutil, subprocess, sys, tempfile
from pathlib import Path

SRC=Path(__file__).resolve().parent

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def update_manifest(root, filename):
    m=json.loads((root/"manifest.json").read_text(encoding="utf-8"))
    for item in m["files"]:
        if item["name"]==filename:
            item["sha256"]=sha(root/filename)
    (root/"manifest.json").write_text(json.dumps(m,indent=2,ensure_ascii=False),encoding="utf-8")

def run_variant(name, mutate, expected_substring):
    with tempfile.TemporaryDirectory() as td:
        dst=Path(td)/"pkg"
        shutil.copytree(SRC,dst,ignore=shutil.ignore_patterns("VERIFIER_OUTPUT.txt","SELFTEST_OUTPUT.txt"))
        mutate(dst)
        p=subprocess.run([sys.executable,"-S",str(dst/"verify_spec.py")],capture_output=True,text=True,cwd=dst)
        out=p.stdout+p.stderr
        ok=expected_substring in out
        print(f"{name}: {'PASS' if ok else 'FAIL'}")
        if not ok:
            print(out)
            raise SystemExit(1)

def noop(root): pass

def approve_flags_only(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    for d in r["decisions"]: d["status"]="approved"
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def empty_decisions(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    r["decisions"]=[]
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def empty_m0(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    r["milestone_profiles"]["M0"]["requirements"]=[]
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def fake_prep(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    r["pre_p01_artifacts"]=[{"id":f"FAKE-{i}","name":"x"} for i in range(9)]
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def invert_precedence(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    r["spec"]["precedence"]=list(reversed(r["spec"]["precedence"]))
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def remove_acceptance_contract(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    r["contracts"].remove("AcceptanceRecord")
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")

def proper_spec_approval(root):
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    a=json.loads((root/"acceptance_registry.json").read_text(encoding="utf-8"))
    for d in r["decisions"]: d["status"]="approved"
    for rec in a["records"]:
        if rec["artifact_type"]=="decision":
            rec["status"]="accepted"
            rec["accepted_by"]="human-reviewer"
            rec["accepted_at"]="2026-09-12T16:00:00+01:00"
            rec["evidence_refs"]=["review://spec-0.5"]
    (root/"spec_registry.json").write_text(json.dumps(r,indent=2,ensure_ascii=False),encoding="utf-8")
    (root/"acceptance_registry.json").write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"spec_registry.json")
    update_manifest(root,"acceptance_registry.json")


def proper_pre_p01_ready(root):
    proper_spec_approval(root)
    r=json.loads((root/"spec_registry.json").read_text(encoding="utf-8"))
    a=json.loads((root/"acceptance_registry.json").read_text(encoding="utf-8"))
    prep={x["id"]:x for x in r["pre_p01_artifacts"]}
    for rec in a["records"]:
        if rec["artifact_type"]=="pre_p01_artifact":
            aid=rec["artifact_id"]
            path=f"pre_p01/{aid}.md"
            full=root/path
            full.parent.mkdir(parents=True,exist_ok=True)
            full.write_text(f"# {prep[aid]['name']}\n\nselftest artifact\n",encoding="utf-8")
            rec["artifact_path"]=path
            rec["artifact_revision"]="0.5-test"
            rec["artifact_hash"]=sha(full)
            rec["status"]="accepted"
            rec["accepted_by"]="human-reviewer"
            rec["accepted_at"]="2026-09-12T16:10:00+01:00"
            rec["evidence_refs"]=["review://pre-p01-selftest"]
    (root/"acceptance_registry.json").write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"acceptance_registry.json")

def invalidated_decision_acceptance(root):
    proper_spec_approval(root)
    a=json.loads((root/"acceptance_registry.json").read_text(encoding="utf-8"))
    for rec in a["records"]:
        if rec["artifact_type"]=="decision" and rec["artifact_id"]=="D-POLICY":
            rec["status"]="invalidated"
            break
    (root/"acceptance_registry.json").write_text(json.dumps(a,indent=2,ensure_ascii=False),encoding="utf-8")
    update_manifest(root,"acceptance_registry.json")

run_variant("base",noop,"RESULT: CONSISTENT_DRAFT")
run_variant("approve-flags-only",approve_flags_only,"RESULT: FAIL")
run_variant("empty-decisions",empty_decisions,"RESULT: FAIL")
run_variant("empty-M0",empty_m0,"RESULT: FAIL")
run_variant("fake-preP01",fake_prep,"RESULT: FAIL")
run_variant("inverted-precedence",invert_precedence,"RESULT: FAIL")
run_variant("missing-AcceptanceRecord-contract",remove_acceptance_contract,"RESULT: FAIL")
run_variant("proper-spec-approval",proper_spec_approval,"RESULT: SPEC_APPROVED_NOT_PRE_P01_READY")
run_variant("invalidated-decision-acceptance",invalidated_decision_acceptance,"RESULT: FAIL")
run_variant("proper-preP01-ready",proper_pre_p01_ready,"RESULT: PRE_P01_READY")
print("ALL SELFTESTS PASS")
