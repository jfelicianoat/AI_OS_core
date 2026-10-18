"""Recorrido E2E: AI OS Core frente a los datos REALES de ChatyGPT, Knowledge Orchestrator,
Trading AI desktop y Local AI Lab (COPIAS de sus bases, abiertas en sólo lectura).

Complementa a e2e_broker_agora.py y e2e_ecosistema.py. Para cada app, Core:
  - ChatyGPT y Knowledge Orchestrator: recibe como recibos de operación TODAS sus tareas al
    AI Broker y debe recomendar, tarea a tarea, la acción correcta tras una caída (no reenviar
    lo terminado, seguir lo que está en curso, permitir reenviar lo que nunca salió). También
    se comprueba que un recibo tardío no reabre una tarea terminada.
  - Trading AI, Local AI Lab y los flujos de Knowledge Orchestrator: proyecta sus registros como
    recursos y eventos full_state y el estado canónico debe coincidir con el origen.
LARM no entra: hoy sólo es especificación y prompts, no hay programa que gobernar.

Uso: python e2e_resto_apps.py <core_url> <carpeta_con_copias>
  La carpeta contiene chatygpt.db, ko.db, trading_ai.db y lab_state.db.
  Variable opcional AI_OS_API_TOKEN: si Core la tiene, se manda el mismo Bearer.
"""
import collections, hashlib, json, os, sqlite3, sys, uuid
import httpx

CORE, COPIES = sys.argv[1], sys.argv[2]
run = uuid.uuid4().hex[:8]
headers = {"Authorization": f"Bearer {os.environ['AI_OS_API_TOKEN']}"} if os.environ.get("AI_OS_API_TOKEN") else {}
core = httpx.Client(base_url=CORE, timeout=30, headers=headers)
ok_count = 0


def step(name, cond, detail=""):
    global ok_count
    print(f"[{'OK ' if cond else 'FALLO'}] {name} {detail}")
    if not cond:
        sys.exit(1)
    ok_count += 1


def ro(name):
    conn = sqlite3.connect(f"file:{COPIES}/{name}?mode=ro", uri=True)
    conn.row_factory = sqlite3.Row
    return conn


def register(service_id, name, caps):
    r = core.post("/api/v1/services", json={"service_id": service_id, "name": name, "base_url": "http://127.0.0.1:1",
                                            "health_status": "unknown", "capabilities": caps})
    step(f"registrar {name} en Core", r.status_code == 201, r.text[:80])


EXPECTED = {"succeeded": "reconstruct_state_no_resend", "accepted": "follow_up_no_resend",
            "in_progress": "follow_up_no_resend", "failed_terminal": "do_not_resend_without_new_decision",
            "cancelled": "do_not_resend_without_new_decision", None: "retry_allowed"}


def receipts_check(app, rows):
    """rows: (operation_id, estado Core o None si nunca se envió, evidencia). Devuelve el resumen."""
    seen = collections.Counter()
    wrong = []
    for op, status, evidence in rows:
        op = f"{app}:{op}:{run}"
        if status is not None:
            r = core.post("/api/v1/operations/receipts", json={"operation_id": op, "receiver_service": "ai_broker",
                                                              "status": status, "evidence": evidence})
            if r.status_code != 201:
                wrong.append((op, "receipt", r.status_code))
                continue
        action = core.post("/api/v1/operations/status", json={"operation_id": op, "target_service_id": "ai_broker"}).json()["recommended_action"]
        seen[(status, action)] += 1
        if action != EXPECTED[status]:
            wrong.append((op, status, action))
    return seen, wrong


def project(app, stream, records):
    """records: (resource_id, resource_type, payload). Proyecta y compara con el origen."""
    bad = []
    for seq, (rid, rtype, payload) in enumerate(records, start=1):
        rid = f"{app}:{rid}:{run}"
        if core.put("/api/v1/resources", json={"resource_id": rid, "resource_type": rtype, "owner_service": app,
                                               "data": payload}).status_code != 200:
            bad.append((rid, "resource"))
        digest = hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()
        ev = core.post("/api/v1/events/inbox", json={"event_id": f"ev_{app}_{run}_{seq}", "producer_id": app,
                                                     "stream_id": f"{stream}_{run}", "stream_epoch": 1, "source_sequence": seq,
                                                     "event_type": "full_state", "resource_id": rid, "resource_type": rtype,
                                                     "revision": 1, "payload": payload, "state_digest": digest}).json()
        if not ev["accepted_in_canonical_projection"]:
            bad.append((rid, ev["reason"]))
            continue
        canon = core.get(f"/api/v1/events/canonical/{rid}").json()
        if canon["payload"] != json.loads(json.dumps(payload, default=str)):
            bad.append((rid, "canonical"))
    return bad


step("core /health", core.get("/health").json()["status"] == "healthy")
if headers:
    step("core exige token sin credencial", httpx.get(f"{CORE}/api/v1/services", timeout=10).status_code == 401)

# ============================== ChatyGPT ===================================
print("\n--- ChatyGPT (tareas reales al Broker -> restore) ---")
register("chatygpt", "ChatyGPT", ["chat.conversations"])
db = ro("chatygpt.db")
CHATY = {"completed": "succeeded", "failed": "failed_terminal", "cancelled": "cancelled",
         "queued": "accepted", "running": "in_progress", "routing": "in_progress", "generating": "in_progress"}
rows = []
for t in db.execute("SELECT idempotency_key, remote_task_id, remote_status, local_state FROM broker_tasks"):
    # Sin remote_task_id la petición nunca llegó al Broker: no hay recibo (not_seen)
    status = None if t["remote_task_id"] is None else CHATY[t["remote_status"]]
    rows.append((t["idempotency_key"], status, {"task_id": t["remote_task_id"], "local_state": t["local_state"]}))
seen, wrong = receipts_check("chatygpt", rows)
print("      (estado, acción):", dict(seen))
step(f"Core recomienda la acción correcta para las {len(rows)} tareas de ChatyGPT", not wrong, str(wrong[:3]))
done = next(op for op, st, _ in rows if st == "succeeded")
late = core.post("/api/v1/operations/receipts", json={"operation_id": f"chatygpt:{done}:{run}", "receiver_service": "ai_broker",
                                                     "status": "not_seen"})
step("un recibo tardío no reabre una tarea de ChatyGPT ya completada", late.status_code == 409)
convs = db.execute("SELECT id, title, archived_at, deleted_at FROM conversations ORDER BY id").fetchall()
bad = project("chatygpt", "conversations", [(c["id"], "conversation", {"title": c["title"], "archived": c["archived_at"] is not None,
                                                                         "deleted": c["deleted_at"] is not None}) for c in convs])
step(f"{len(convs)} conversaciones proyectadas = origen", not bad, str(bad[:3]))

# ======================== Knowledge Orchestrator ===========================
print("\n--- Knowledge Orchestrator (tareas al Broker y flujos) ---")
register("knowledge_orchestrator", "Knowledge Orchestrator", ["knowledge.capture"])
db = ro("ko.db")
KO = {"SUCCESS": "succeeded", "CANCELLED": "cancelled", "QUEUED": "accepted", "PROCESSING": "in_progress"}
rows = []
for t in db.execute("SELECT task_id, idempotency_key, broker_task_id, status, error_retryable FROM tasks"):
    if t["status"] == "ERROR":
        # Un error reintentable no es terminal: el propio KO lo volverá a intentar
        status = "in_progress" if t["error_retryable"] else "failed_terminal"
    else:
        status = KO[t["status"]]
    if t["broker_task_id"] is None and status == "accepted":
        status = None  # en cola local, aún sin tarea en el Broker
    rows.append((t["idempotency_key"] or t["task_id"], status, {"task_id": t["broker_task_id"]}))
seen, wrong = receipts_check("ko", rows)
print("      (estado, acción):", dict(seen))
step(f"Core recomienda la acción correcta para las {len(rows)} tareas de KO", not wrong, str(wrong[:3]))
step("KO tiene trabajo vivo y Core manda seguirlo, no reenviarlo",
     any(a == "follow_up_no_resend" for (_, a) in seen) or any(s is None for (s, _) in seen))
wf = db.execute("SELECT workflow_id, status, total_steps, completed_steps, review_status FROM workflows ORDER BY workflow_id").fetchall()
bad = project("knowledge_orchestrator", "workflows", [(w["workflow_id"], "ko_workflow", dict(w)) for w in wf])
step(f"{len(wf)} flujos de KO proyectados = origen", not bad, str(bad[:3]))

# ============================== Trading AI =================================
print("\n--- Trading AI desktop (backtests) ---")
register("trading_ai", "Trading AI desktop", ["trading.backtest"])
db = ro("trading_ai.db")
bt = db.execute("SELECT id, fingerprint, strategy_id, dataset_id, engine_version, status FROM backtest_runs ORDER BY created_at").fetchall()
bad = project("trading_ai", "backtests", [(b["id"], "backtest_run", dict(b)) for b in bt])
step(f"{len(bt)} backtests proyectados = origen", not bad, str(bad[:3]))
# Reproyectar el mismo backtest con otra huella en la misma revisión es una contradicción (C03)
b0 = bt[0]
seq = len(bt) + 1
contra = core.post("/api/v1/events/inbox", json={"event_id": f"ev_trading_ai_{run}_{seq}", "producer_id": "trading_ai",
                                                 "stream_id": f"backtests_{run}", "stream_epoch": 1, "source_sequence": seq,
                                                 "event_type": "full_state", "resource_id": f"trading_ai:{b0['id']}:{run}",
                                                 "resource_type": "backtest_run", "revision": 1,
                                                 "payload": {**dict(b0), "fingerprint": "alterada"}, "state_digest": "alterada"}).json()
step("un backtest con otra huella y la misma revisión va a cuarentena", contra["quarantine"], contra["reason"] or "")
step("la proyección del backtest sigue siendo la original",
     core.get(f"/api/v1/events/canonical/trading_ai:{b0['id']}:{run}").json()["payload"]["fingerprint"] == b0["fingerprint"])

# ============================== Local AI Lab ===============================
print("\n--- Local AI Lab (registros de experimentos) ---")
register("local_ai_lab", "Local AI Lab", ["lab.experiments"])
db = ro("lab_state.db")
recs = db.execute("SELECT record_id, category, title, status, artifact_sha256 FROM product_records ORDER BY created_at").fetchall()
bad = project("local_ai_lab", "records", [(r["record_id"], "lab_record", dict(r)) for r in recs])
step(f"{len(recs)} registros de Local AI Lab proyectados = origen", not bad, str(bad[:3]))

services = {s["service_id"] for s in core.get("/api/v1/services").json()}
step("Core conoce las cuatro apps", {"chatygpt", "knowledge_orchestrator", "trading_ai", "local_ai_lab"} <= services, str(sorted(services)))
gaps = [g for g in core.get("/api/v1/events/gaps").json() if g["stream_id"].endswith(run)]
step("sin huecos de secuencia en los flujos del recorrido", not gaps)
print(f"\nE2E resto de apps completo: {ok_count} comprobaciones OK. run={run}")
