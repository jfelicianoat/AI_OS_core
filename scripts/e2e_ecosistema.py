"""Recorrido E2E: AI OS Core como director del resto de apps del TFM.

Complementa a e2e_broker_agora.py. Aquí Core:
  1. Proyecta los resultados REALES de Model_Drift como certificaciones y decide con ellas
     qué modelo puede usarse (política que niega modelos no certificados).
  2. Gobierna un run REAL de Athena (que a su vez usa el AI Broker) con el modelo que Core
     autoriza: política, presupuesto, plan, recibos, idempotencia y proyección del run.
  3. Proyecta las tareas REALES de Gestión Tareas IA (desde una COPIA de su base) como meta,
     recursos, relaciones y eventos, y comprueba que el estado canónico coincide con el origen.

Uso:
  python e2e_ecosistema.py <core_url> <athena_url> <athena_token> <model_drift_sqlite> <copia_gti_sqlite> <workspace>
  Variable opcional AI_OS_API_TOKEN: si Core la tiene, el guion manda el mismo Bearer.

Model_Drift y Gestión Tareas IA sólo se leen (modo ro). La regla para convertir resultados de
Model_Drift en veredicto es de este guion, no de Model_Drift: media de pass_rate sobre casos
aplicables >= 0.8 con al menos 3 casos -> CERTIFIED; < 0.5 -> REJECTED; si no, INDETERMINATE.
"""
import hashlib, json, os, sqlite3, sys, time, uuid
from pathlib import Path
import httpx

CORE, ATHENA, ATHENA_TOKEN, DRIFT_DB, GTI_DB, WORKSPACE = sys.argv[1:7]
run = uuid.uuid4().hex[:8]
core_headers = {"Authorization": f"Bearer {os.environ['AI_OS_API_TOKEN']}"} if os.environ.get("AI_OS_API_TOKEN") else {}
core = httpx.Client(base_url=CORE, timeout=30, headers=core_headers)
athena = httpx.Client(base_url=ATHENA, timeout=30, headers={"Authorization": f"Bearer {ATHENA_TOKEN}"})
ok_count = 0


def step(name, cond, detail=""):
    global ok_count
    print(f"[{'OK ' if cond else 'FALLO'}] {name} {detail}")
    if not cond:
        sys.exit(1)
    ok_count += 1


def post(path, body):
    return core.post(path, json=body)


def ro(path):
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


# 0. Core y su autenticación
step("core /health", core.get("/health").json()["status"] == "healthy")
if core_headers:
    anon = httpx.get(f"{CORE}/api/v1/goals", timeout=10)
    step("core exige token sin credencial", anon.status_code == 401, str(anon.status_code))

# ========================= 1. MODEL_DRIFT ==================================
print("\n--- Model_Drift (resultados reales -> certificaciones) ---")
md = ro(DRIFT_DB)
rows = md.execute("""
    SELECT cr.model_key, r.suite_id, COUNT(DISTINCT cr.run_id) AS runs,
           SUM(CASE WHEN cr.is_not_applicable = 0 AND cr.case_score IS NOT NULL THEN 1 ELSE 0 END) AS applicable,
           AVG(CASE WHEN cr.is_not_applicable = 0 THEN cr.case_score END) AS mean_pass
    FROM case_result cr JOIN run r USING (run_id)
    WHERE cr.metric = 'pass_rate' GROUP BY cr.model_key, r.suite_id""").fetchall()
step("Model_Drift tiene resultados de pass_rate", len(rows) > 0, f"{len(rows)} modelos")
post("/api/v1/services", {"service_id": "model_drift", "name": "Model Drift", "base_url": "http://127.0.0.1:1",
                          "health_status": "unknown", "capabilities": ["model.certification"]})
verdicts = {}
for row in rows:
    applicable, mean = row["applicable"], row["mean_pass"]
    if applicable >= 3 and mean is not None and mean >= 0.8:
        verdict = "CERTIFIED"
    elif applicable >= 1 and mean is not None and mean < 0.5:
        verdict = "REJECTED"
    else:
        verdict = "INDETERMINATE"
    model = f"{row['model_key']}@e2e-{run}"  # sufijo para no chocar con revisiones de pasadas anteriores
    cap = f"suite:{row['suite_id']}"
    r = post("/api/v1/certifications", {"model_id": model, "capability_id": cap, "version": "1", "source_system": "model_drift",
                                         "evaluation_verdict": verdict, "is_applicable": verdict == "CERTIFIED", "revision": row["runs"]})
    if r.status_code != 201:
        step("certificación registrada", False, r.text[:150])
    verdicts[row["model_key"]] = (verdict, model, cap)
    print(f"      {row['model_key']:45s} casos={applicable} media={mean if mean is None else round(mean, 2)} -> {verdict}")
step("veredictos proyectados en Core", all(
    core.get(f"/api/v1/certifications/{m}/{c}/1").json()["evaluation_verdict"] == v for v, m, c in verdicts.values()))
late = post("/api/v1/certifications", {**{"model_id": next(iter(verdicts.values()))[1], "capability_id": next(iter(verdicts.values()))[2],
                                          "version": "1", "evaluation_verdict": "CERTIFIED", "is_applicable": True},
                                       "source_system": "otra_app", "revision": 99})
step("otra app no puede reescribir un veredicto de Model_Drift", late.status_code == 409)

mscope = f"llm:model:{run}"
post("/api/v1/policies", {"policy_id": f"pol_cert_{run}", "policy_key": "solo_modelos_certificados", "scope": mscope,
                          "decision_if_matched": "DENY",
                          "conditions": [{"field": "certification", "operator": "not_equals", "value": "CERTIFIED"}]})
post("/api/v1/policies", {"policy_id": f"pol_mbase_{run}", "policy_key": "base", "scope": mscope,
                          "decision_if_matched": "ALLOW", "unconditional": True})
seen = set()
for model_key, (verdict, model, cap) in verdicts.items():
    cert = core.get(f"/api/v1/certifications/{model}/{cap}/1").json()["evaluation_verdict"]
    auth = post("/api/v1/policies/evaluate", {"scope": mscope, "context": {"certification": cert, "model": model_key}}).json()["authorization"]
    expected = "ALLOW" if verdict == "CERTIFIED" else "DENY"
    if auth != expected:
        step(f"decisión para {model_key}", False, f"{auth} != {expected}")
    seen.add((verdict, auth))
print("      combinaciones veredicto/decisión:", sorted(seen))
step("Core sólo autoriza modelos certificados por Model_Drift", ("CERTIFIED", "ALLOW") in seen and any(a == "DENY" for _, a in seen))
step("modelo sin certificación -> INDETERMINATE",
     post("/api/v1/policies/evaluate", {"scope": mscope, "context": {"model": "desconocido"}}).json()["authorization"] == "INDETERMINATE")
if "ollama/local/lfm2:24b" in verdicts:
    print(f"      nota: lfm2:24b (el que respondió en el E2E del Broker) sale {verdicts['ollama/local/lfm2:24b'][0]} para facturación")

# =========================== 2. ATHENA =====================================
print("\n--- Athena (run real, que usa el AI Broker) ---")
health = athena.get("/v1/health").json()
step("athena /v1/health", health.get("status") == "ok", json.dumps(health))
step("athena acepta su token", athena.get("/v1/auth/check").status_code == 200)
r = post("/api/v1/services", {"service_id": "athena", "name": "Athena runtime", "base_url": ATHENA,
                              "version": str(health.get("wire_version")), "capabilities": ["agent.run"]})
step("registrar Athena en Core", r.status_code == 201, r.text[:100])
post("/api/v1/capabilities", {"capability_id": "agent.run", "name": "Run agéntico", "provider_service_id": "athena",
                              "description": "POST /v1/runs"})

gid = f"goal_athena_{run}"
post("/api/v1/goals", {"title": "Inventario del espacio de trabajo con Athena", "description": "E2E ecosistema", "goal_id": gid})
oid = post("/api/v1/objectives", {"goal_id": gid, "title": "Contar las líneas de notas.txt"}).json()["id"]

scope = f"athena:run:{run}"
post("/api/v1/policies", {"policy_id": f"pol_wr_{run}", "policy_key": "escritura_requiere_aprobacion", "scope": scope,
                          "decision_if_matched": "REQUIRE_APPROVAL",
                          "conditions": [{"field": "writes", "operator": "not_equals", "value": "off"}]})
post("/api/v1/policies", {"policy_id": f"pol_ex_{run}", "policy_key": "ejecucion_prohibida", "scope": scope,
                          "decision_if_matched": "DENY",
                          "conditions": [{"field": "exec", "operator": "equals", "value": "allow"}]})
post("/api/v1/policies", {"policy_id": f"pol_base_{run}", "policy_key": "base", "scope": scope,
                          "decision_if_matched": "ALLOW", "unconditional": True, "obligations": ["audit_trace"]})
policy = {"writes": "off", "exec": "off"}
dec = post("/api/v1/policies/evaluate", {"scope": scope, "context": policy, "principal_id": "e2e"}).json()
step("política: Athena sólo lectura -> ALLOW", dec["authorization"] == "ALLOW" and dec["executable"], dec["trace_id"])
step("política: Athena con escritura -> REQUIRE_APPROVAL",
     post("/api/v1/policies/evaluate", {"scope": scope, "context": {"writes": "ask", "exec": "off"}}).json()["authorization"] == "REQUIRE_APPROVAL")
step("política: Athena con exec=allow -> DENY",
     post("/api/v1/policies/evaluate", {"scope": scope, "context": {"writes": "off", "exec": "allow"}}).json()["authorization"] == "DENY")

acc = f"athena_{run}"
post("/api/v1/budget/accounts", {"account_id": acc, "balance": 1.0})
res = post("/api/v1/budget/reserve", {"account_id": acc, "amount": 0.2}).json()
plan = post("/api/v1/planner/proposals", {"goal_id": gid, "requested_autonomy": "A3", "policy_decision": dec, "tasks": [
    {"task_id": "inventario", "title": "Inventario", "description": "Run de sólo lectura", "assigned_service": "athena"}]}).json()
decision = post(f"/api/v1/planner/proposals/{plan['proposal_id']}/decision", {"applicable_ceilings": ["A3"]}).json()
step("plan para Athena aprobado en A3", decision["approved_for_dispatch"], decision["reasons"][0])

ws = Path(WORKSPACE)
ws.mkdir(parents=True, exist_ok=True)
(ws / "notas.txt").write_text("alfa\nbeta\ngamma\ndelta\n", encoding="utf-8")
before = hashlib.sha256((ws / "notas.txt").read_bytes()).hexdigest()
op_id = f"op_athena_{run}"
st = post("/api/v1/operations/status", {"operation_id": op_id, "target_service_id": "athena"}).json()
step("restore antes de enviar a Athena: retry_allowed", st["recommended_action"] == "retry_allowed")
# El director elige el modelo: de los que ofrece Athena, el primero que Core autoriza
# según la certificación proyectada desde Model_Drift.
offered = [m["name"] for m in athena.get("/v1/models").json().get("models", [])]
chosen, denied = None, []
for name in offered:
    entry = verdicts.get(f"ollama/local/{name}")
    cert = core.get(f"/api/v1/certifications/{entry[1]}/{entry[2]}/1").json()["evaluation_verdict"] if entry else None
    ctx = {"model": name, **({"certification": cert} if cert else {})}
    auth = post("/api/v1/policies/evaluate", {"scope": mscope, "context": ctx}).json()["authorization"]
    print(f"      Athena ofrece {name:25s} certificación={cert} -> {auth}")
    if auth == "ALLOW" and chosen is None:
        chosen = name
    elif auth != "ALLOW":
        denied.append(name)
step("Core elige un modelo certificado para Athena", chosen is not None, f"{chosen}; descartados {denied}")
step("Core descarta los modelos no certificados que ofrece Athena", len(denied) >= 1)
body = {"model": chosen, "profile": "questions", "objective": "Read notas.txt in the workspace and answer with the exact number of lines it has. Do not modify any file.",
        "workspace": str(ws), "writes": policy["writes"], "exec": policy["exec"]}
created = athena.post("/v1/runs", json=body, headers={"Idempotency-Key": f"ai-os-core:{op_id}"})
step("Athena acepta el run", created.status_code in (200, 201, 202), created.text[:200])
run_id = created.json()["run_id"]
post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "athena", "status": "accepted",
                                     "evidence": {"run_id": run_id}})
again = athena.post("/v1/runs", json=body, headers={"Idempotency-Key": f"ai-os-core:{op_id}"})
step("Athena: misma clave de idempotencia -> mismo run", again.json().get("run_id") == run_id, str(again.status_code))

deadline = time.time() + 900
seq, last = 0, None
while time.time() < deadline:
    snap = athena.get(f"/v1/runs/{run_id}").json()
    status = snap.get("status")
    if status != last:
        last = status
        seq += 1
        print(f"      athena: {status}")
        # Cada cambio de estado del run entra en Core como full_state ordenado
        ev = post("/api/v1/events/inbox", {"event_id": f"ev_ath_{run}_{seq}", "producer_id": "athena", "stream_id": f"runs_{run}",
                                           "stream_epoch": 1, "source_sequence": seq, "event_type": "full_state",
                                           "resource_id": f"athena_run:{run_id}", "resource_type": "athena_run", "revision": seq,
                                           "payload": {"status": status}, "state_digest": status}).json()
        if not ev["accepted_in_canonical_projection"]:
            step("evento de Athena aceptado", False, json.dumps(ev))
        if status in ("running", "in_progress"):
            post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "athena", "status": "in_progress",
                                                 "evidence": {"run_id": run_id}})
    if status in ("completed", "failed", "cancelled", "recovery_pending"):
        break
    time.sleep(3)
step("Athena termina el run", last == "completed", f"{last}")
# La API de Athena no expone el texto final de la respuesta; la evidencia está en el historial
events = athena.get(f"/v1/runs/{run_id}/history").json()["events"]
models_used = {e["payload"].get("model") for e in events if e["name"] == "model.completed"}
reads = [e["payload"]["display"]["facts"] for e in events
         if e["name"] == "tool.completed" and e["payload"].get("tool_name") == "read_file"]
print("      modelos que respondieron:", models_used, "| lecturas:", [(f.get("path"), f.get("line_count")) for f in reads])
step("Athena usó el modelo que eligió Core", models_used == {chosen}, str(models_used))
step("Athena leyó notas.txt y vio sus 4 líneas", any(f.get("path") == "notas.txt" and f.get("line_count") == 4 for f in reads))
answer = json.dumps({"verification": snap.get("verification"), "reads": reads}, sort_keys=True)
step("Athena no modificó el espacio de trabajo", hashlib.sha256((ws / "notas.txt").read_bytes()).hexdigest() == before)
post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "athena", "status": "succeeded",
                                     "result_digest": hashlib.sha256(answer.encode()).hexdigest(), "evidence": {"run_id": run_id}})
st = post("/api/v1/operations/status", {"operation_id": op_id, "target_service_id": "athena"}).json()
step("restore tras el run: reconstruct_state_no_resend", st["recommended_action"] == "reconstruct_state_no_resend")
canon = core.get(f"/api/v1/events/canonical/athena_run:{run_id}").json()
step("estado canónico del run en Core = completed", canon["payload"]["status"] == "completed", f"rev {canon['revision']}")
post("/api/v1/budget/consume", {"reservation_id": res["reservation_id"]})
step("presupuesto de Athena consumido", core.get(f"/api/v1/budget/accounts/{acc}").json()["balance"] == 0.8)
core.put("/api/v1/resources", json={"resource_id": oid, "resource_type": "objective", "owner_service": "ai_os_core"})
core.put("/api/v1/resources", json={"resource_id": f"athena_run:{run_id}", "resource_type": "athena_run", "owner_service": "athena"})
step("grafo: objetivo -> run de Athena",
     post("/api/v1/resources/relations", {"source_id": oid, "target_id": f"athena_run:{run_id}", "relation_type": "fulfilled_by"}).status_code == 201)
step("identity binding operación -> run_id de Athena",
     core.put("/api/v1/identity-bindings", json={"global_id": op_id, "native_id": run_id, "source_system": "athena"}).json()["native_id"] == run_id)
core.patch(f"/api/v1/objectives/{oid}/status", json={"status": "completed", "principal_id": "e2e"})

# ======================= 3. GESTIÓN TAREAS IA ==============================
print("\n--- Gestión Tareas IA (copia de su base -> meta, recursos y eventos) ---")
gti = ro(GTI_DB)
projects = gti.execute("SELECT id, name FROM projects").fetchall()
tasks = gti.execute("SELECT id, title, status, project_id, importance, urgency, due_date, updated_at FROM tasks "
                    "WHERE deleted_at IS NULL ORDER BY updated_at, id").fetchall()
deps = gti.execute("SELECT task_id, depends_on_task_id FROM task_dependencies").fetchall()
step("copia de GTI legible", len(tasks) > 0, f"{len(projects)} proyectos, {len(tasks)} tareas, {len(deps)} dependencias")
post("/api/v1/services", {"service_id": "gestion_tareas", "name": "Gestión Tareas IA", "base_url": "http://127.0.0.1:1",
                          "health_status": "unknown", "capabilities": ["tasks.plan"]})
status_map = {"completed": "completed", "in_progress": "active", "pending": "pending", "cancelled": "cancelled"}
for p in projects:
    pg = f"gti_project_{p['id']}_{run}"
    post("/api/v1/goals", {"title": p["name"], "description": "Proyecto de Gestión Tareas IA", "goal_id": pg, "owner_service": "gestion_tareas"})
    core.put("/api/v1/resources", json={"resource_id": pg, "resource_type": "gti_project", "owner_service": "gestion_tareas"})
mismatch, seq = [], 0
for t in tasks:
    rid = f"gti_task:{t['id']}:{run}"
    data = {"title": t["title"], "status": t["status"], "importance": t["importance"], "urgency": t["urgency"], "due_date": t["due_date"]}
    if core.put("/api/v1/resources", json={"resource_id": rid, "resource_type": "gti_task", "owner_service": "gestion_tareas",
                                           "data": data}).status_code != 200:
        mismatch.append(("resource", t["id"]))
    if t["project_id"] is not None:
        post("/api/v1/resources/relations", {"source_id": f"gti_project_{t['project_id']}_{run}", "target_id": rid, "relation_type": "contains"})
    seq += 1
    digest = hashlib.sha256(json.dumps(data, sort_keys=True).encode()).hexdigest()
    ev = post("/api/v1/events/inbox", {"event_id": f"ev_gti_{run}_{seq}", "producer_id": "gestion_tareas", "stream_id": f"tasks_{run}",
                                       "stream_epoch": 1, "source_sequence": seq, "event_type": "full_state", "resource_id": rid,
                                       "resource_type": "gti_task", "revision": 1, "payload": data, "state_digest": digest}).json()
    if not ev["accepted_in_canonical_projection"]:
        mismatch.append(("event", t["id"], ev["reason"]))
for d in deps:
    post("/api/v1/resources/relations", {"source_id": f"gti_task:{d['task_id']}:{run}", "target_id": f"gti_task:{d['depends_on_task_id']}:{run}",
                                         "relation_type": "depends_on"})
step("todas las tareas proyectadas y aceptadas", not mismatch, str(mismatch[:3]))
diff = [t["id"] for t in tasks
        if core.get(f"/api/v1/events/canonical/gti_task:{t['id']}:{run}").json()["payload"]["status"] != t["status"]]
step("estado canónico de cada tarea = base de GTI", not diff, f"{len(tasks)} comparadas, {len(diff)} distintas")
for p in projects:
    in_project = sum(1 for t in tasks if t["project_id"] == p["id"])
    if not in_project:
        print(f"      nota: el proyecto '{p['name']}' no tiene tareas asignadas en GTI; su relación no se comprueba")
        continue
    rel = core.get(f"/api/v1/resources/gti_project_{p['id']}_{run}").json()["relations"]
    step(f"grafo: proyecto '{p['name']}' -> sus tareas", len(rel) == in_project, f"{len(rel)} relaciones / {in_project} tareas")
# Un cambio real de estado (simulado en Core, no en GTI) con revisión 2 actualiza la proyección
t0 = tasks[0]
seq += 1
post("/api/v1/events/inbox", {"event_id": f"ev_gti_{run}_{seq}", "producer_id": "gestion_tareas", "stream_id": f"tasks_{run}",
                              "stream_epoch": 1, "source_sequence": seq, "event_type": "full_state", "resource_id": f"gti_task:{t0['id']}:{run}",
                              "resource_type": "gti_task", "revision": 2, "payload": {"status": "completed"}, "state_digest": "completed"})
step("cambio posterior de una tarea actualiza la proyección",
     core.get(f"/api/v1/events/canonical/gti_task:{t0['id']}:{run}").json()["revision"] == 2)
gaps = [g for g in core.get("/api/v1/events/gaps").json() if g["stream_id"] in (f"tasks_{run}", f"runs_{run}")]
step("sin huecos de secuencia en los flujos del recorrido", not gaps)

print(f"\nE2E ecosistema completo: {ok_count} comprobaciones OK. run={run} athena_run={run_id}")
