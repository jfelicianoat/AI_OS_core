"""Recorrido E2E: AI OS Core gobierna una tarea real en el AI Broker y proyecta el tablero de Agora.

Uso: python e2e_broker_agora.py <core_url> <broker_token> <agora_token>
Agora sólo se lee (no se crean tarjetas: eso encargaría trabajo real al PC IA).
"""
import hashlib, json, os, sys, time, uuid
import httpx

CORE, BROKER_TOKEN, AGORA_TOKEN = sys.argv[1], sys.argv[2], sys.argv[3]
# Desde el 20-oct el Broker solo escucha en HTTPS con su CA propia («AI Broker CA»).
BROKER = os.environ.get("AI_BROKER_URL", "https://192.168.1.52:8765")
BROKER_CA = os.environ.get("AI_BROKER_CA_CERT", "C:/Agora/pki-broker/ca.crt")
AGORA = "https://127.0.0.1:8741"
run = uuid.uuid4().hex[:8]
core = httpx.Client(base_url=CORE, timeout=30,  # AI_OS_API_TOKEN opcional: si Core lo exige, se manda el mismo Bearer
                    headers={"Authorization": f"Bearer {os.environ['AI_OS_API_TOKEN']}"} if os.environ.get("AI_OS_API_TOKEN") else {})
broker = httpx.Client(base_url=BROKER, timeout=30, verify=BROKER_CA, headers={"X-Admin-Token": BROKER_TOKEN})
agora = httpx.Client(base_url=AGORA, timeout=30, verify="C:/Agora/pki/ca.crt",
                     headers={"Authorization": f"Bearer {AGORA_TOKEN}"})
ok_count = 0


def step(name, cond, detail=""):
    global ok_count
    mark = "OK " if cond else "FALLO"
    print(f"[{mark}] {name} {detail}")
    if not cond:
        sys.exit(1)
    ok_count += 1


def post(path, body, **kw):
    r = core.post(path, json=body, **kw)
    return r


# 1. Core vivo y migrado
h = core.get("/health").json(); rd = core.get("/ready").json()
step("core /health y /ready", h["status"] == "healthy" and rd["status"] == "ready", f"v{h['version']} schema={rd['schema_version']}")

# 2. Registro federado de los servicios reales
caps = broker.get("/api/v1/capabilities").json()
step("broker capabilities", "contract_version" in caps, f"contrato {caps['contract_version']}, estrategias {caps.get('strategies')}")
r = post("/api/v1/services", {"service_id": "ai_broker", "name": "AI Broker", "base_url": BROKER,
                              "version": caps["contract_version"], "capabilities": ["llm.task"],
                              "metadata": {"auth_header": "X-Admin-Token"}})
step("registrar AI Broker (IP LAN privada)", r.status_code == 201, r.text[:120])
agora_health = agora.get("/api/v1/health")
step("agora /api/v1/health con token", agora_health.status_code == 200, agora_health.text[:120])
r = post("/api/v1/services", {"service_id": "agora_board", "name": "Agora tablero", "base_url": AGORA,
                              "capabilities": ["agents.cards"]})
step("registrar tablero de Agora (loopback https)", r.status_code == 201)
r = post("/api/v1/capabilities", {"capability_id": "llm.task", "name": "Tarea LLM", "provider_service_id": "ai_broker",
                                  "description": "POST /api/v1/tasks con sondeo", "version": caps["contract_version"]})
step("registrar capacidad llm.task", r.status_code == 201)
r = post("/api/v1/capabilities", {"capability_id": "x", "name": "x", "provider_service_id": "fantasma", "description": "x"})
step("capacidad de proveedor inexistente rechazada", r.status_code == 400)

# 3. Meta y objetivo
gid = f"goal_e2e_{run}"
post("/api/v1/goals", {"title": "Resumen asistido por el Broker", "description": "E2E", "goal_id": gid})
r = post("/api/v1/objectives", {"goal_id": gid, "title": "Obtener resumen de una línea"})
oid = r.json()["id"]
step("meta + objetivo", r.status_code == 201, oid)

# 4. Políticas para invocar el Broker
scope = f"broker:invoke:{run}"
post("/api/v1/policies", {"policy_id": f"pol_conf_{run}", "policy_key": "confidencial_requiere_aprobacion", "scope": scope,
                          "decision_if_matched": "REQUIRE_APPROVAL",
                          "conditions": [{"field": "data_classification", "operator": "in", "value": ["confidential", "local_only"]}]})
post("/api/v1/policies", {"policy_id": f"pol_cost_{run}", "policy_key": "coste_maximo", "scope": scope,
                          "decision_if_matched": "DENY", "conditions": [{"field": "estimated_cost", "operator": "greater_than", "value": 5}]})
post("/api/v1/policies", {"policy_id": f"pol_audit_{run}", "policy_key": "auditar_siempre", "scope": scope,
                          "decision_if_matched": "ALLOW", "unconditional": True, "obligations": ["audit_trace"],
                          "constraints": {"max_output_tokens": 600}})
ctx_ok = {"data_classification": "internal", "estimated_cost": 0.5}
dec = post("/api/v1/policies/evaluate", {"scope": scope, "context": ctx_ok, "principal_id": "e2e"}).json()
step("política: internal y barato -> ALLOW ejecutable", dec["authorization"] == "ALLOW" and dec["executable"], json.dumps(dec))
dec_conf = post("/api/v1/policies/evaluate", {"scope": scope, "context": {"data_classification": "confidential", "estimated_cost": 0.5}}).json()
step("política: confidencial -> REQUIRE_APPROVAL", dec_conf["authorization"] == "REQUIRE_APPROVAL" and not dec_conf["executable"])
dec_unknown = post("/api/v1/policies/evaluate", {"scope": scope, "context": {"data_classification": "internal"}}).json()
step("política: coste desconocido -> INDETERMINATE", dec_unknown["authorization"] == "INDETERMINATE", str(dec_unknown["unknown_inputs"]))

# 5. Presupuesto
acc = f"broker_{run}"
post("/api/v1/budget/accounts", {"account_id": acc, "balance": 2.0})
res = post("/api/v1/budget/reserve", {"account_id": acc, "amount": 0.5}).json()
step("reserva de presupuesto", res["status"] == "reserved", res["reservation_id"])

# 6. Petición al Broker y aprobación exact_action sobre su digest
broker_body = {
    "idempotency_key": f"ai-os-core:e2e:{run}",
    "request_id": f"core-{run}",
    "content": {"prompt": "Responde en una sola frase: ¿para qué sirve un plano de control (control plane) en un sistema distribuido?",
                "metadata": {"origin": "ai_os_core_e2e"}},
    "generation": {"max_output_tokens": dec["constraints"]["max_output_tokens"], "temperature": 0.2},
    "risk": {"data_classification": ctx_ok["data_classification"]},
}
digest = hashlib.sha256(json.dumps(broker_body, sort_keys=True).encode()).hexdigest()
auth_id = f"auth_{run}"
post("/api/v1/approvals", {"authorization_id": auth_id, "scope": scope, "max_uses": 1, "expected_digest": digest,
                           "expires_at": "2099-01-01T00:00:00Z"})
op_id = f"op_broker_{run}"
r = post("/api/v1/approvals/use", {"use_id": f"use_{run}", "authorization_id": auth_id, "operation_id": op_id, "operation_digest": digest})
step("uso de aprobación exact_action comprometido", r.status_code == 200)
r = post("/api/v1/approvals/use", {"use_id": f"use2_{run}", "authorization_id": auth_id, "operation_id": "otra", "operation_digest": "manipulado"})
step("digest manipulado rechazado", r.status_code == 403)

# 7. Paquete de contexto y plan
pkg = post("/api/v1/context/packages", {"goal_id": gid, "classification_level": "INTERNAL", "payload": {"prompt_digest": digest},
                                        "resources": [{"resource_id": oid, "resource_type": "objective", "owner_service": "ai_os_core"}]}).json()
step("ContextPackage creado", "snapshot_hash" in pkg, pkg["snapshot_hash"][:16])
plan = post("/api/v1/planner/proposals", {"goal_id": gid, "requested_autonomy": "A3", "policy_decision": dec, "tasks": [
    {"task_id": "invocar_broker", "title": "Invocar el Broker", "description": "Tarea LLM", "assigned_service": "ai_broker"},
    {"task_id": "proyectar_agora", "title": "Leer tablero", "description": "Snapshot", "assigned_service": "agora_board"}]}).json()
decision = post(f"/api/v1/planner/proposals/{plan['proposal_id']}/decision", {"applicable_ceilings": ["A3", "A4"]}).json()
step("plan aprobado para despacho en A3", decision["approved_for_dispatch"] and decision["effective_autonomy"] == "A3", decision["reasons"][0])
forged = post("/api/v1/planner/proposals", {"goal_id": gid, "requested_autonomy": "A3",
                                            "policy_decision": {"authorization": "ALLOW", "executable": True},
                                            "tasks": [{"task_id": "x", "title": "x", "description": "x", "assigned_service": "ai_broker"}]})
step("plan con ALLOW no emitido por el Core rechazado (0.2.1)", forged.status_code == 400, str(forged.status_code))

# 8. Restore antes de enviar: not_seen -> se puede enviar
st = post("/api/v1/operations/status", {"operation_id": op_id, "target_service_id": "ai_broker"}).json()
step("restore antes de enviar: retry_allowed", st["recommended_action"] == "retry_allowed")
post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "ai_broker", "status": "accepted"})

# 9. Invocación REAL al Broker
created = broker.post("/api/v1/tasks", json=broker_body)
step("broker acepta la tarea", created.status_code in (200, 202), created.text[:200])
task_id = created.json()["task_id"]
post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "ai_broker", "status": "in_progress",
                                     "evidence": {"task_id": task_id}})
st = post("/api/v1/operations/status", {"operation_id": op_id, "target_service_id": "ai_broker"}).json()
step("restore en curso: follow_up_no_resend", st["recommended_action"] == "follow_up_no_resend")
deadline = time.time() + 600
seq = 0
last_status = None
while time.time() < deadline:
    t = broker.get(f"/api/v1/tasks/{task_id}").json()
    if t["status"] != last_status:
        last_status = t["status"]
        print(f"      broker: {last_status}")
    if t["status"] in ("completed", "failed", "cancelled", "expired"):
        break
    time.sleep(4)
step("broker termina la tarea", t["status"] == "completed", t["status"])
result = t.get("result") or {}
answer = result.get("assistant_content") or result.get("content") or json.dumps(result)[:300]
print("      respuesta:", str(answer)[:300].replace("\n", " "))
print("      modelo:", result.get("model_used") or result.get("models_used"))
result_digest = hashlib.sha256(str(answer).encode()).hexdigest()

# 10. Recibo final, evento canónico, presupuesto consumido
post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "ai_broker", "status": "succeeded",
                                     "result_digest": result_digest, "evidence": {"task_id": task_id}})
st = post("/api/v1/operations/status", {"operation_id": op_id, "target_service_id": "ai_broker"}).json()
step("restore tras éxito: reconstruct_state_no_resend", st["recommended_action"] == "reconstruct_state_no_resend")
late_receipt = post("/api/v1/operations/receipts", {"operation_id": op_id, "receiver_service": "ai_broker", "status": "not_seen"})
step("recibo tardío no reabre una operación ya terminada (0.2.1)", late_receipt.status_code == 409, str(late_receipt.status_code))
res_id = f"broker_task:{task_id}"
for rev, status in ((1, "queued"), (2, "completed")):
    seq += 1
    ev = {"event_id": f"ev_{run}_{seq}", "producer_id": "ai_broker", "stream_id": f"tasks_{run}", "stream_epoch": 1,
          "source_sequence": seq, "event_type": "full_state", "resource_id": res_id, "resource_type": "broker_task",
          "revision": rev, "payload": {"status": status}, "state_digest": f"{status}"}
    post("/api/v1/events/inbox", ev)
late = post("/api/v1/events/inbox", {"event_id": f"ev_{run}_late", "producer_id": "ai_broker", "stream_id": f"tasks_{run}",
                                     "stream_epoch": 1, "source_sequence": 3, "event_type": "full_state", "resource_id": res_id,
                                     "resource_type": "broker_task", "revision": 1, "payload": {"status": "queued"}, "state_digest": "queued"})
canon = core.get(f"/api/v1/events/canonical/{res_id}").json()
step("proyección canónica no retrocede ante evento tardío (C02)", canon["revision"] == 2 and canon["payload"]["status"] == "completed")
post("/api/v1/budget/consume", {"reservation_id": res["reservation_id"]})
bal = core.get(f"/api/v1/budget/accounts/{acc}").json()
step("presupuesto consumido", bal["balance"] == 1.5 and bal["reserved"] == 0, json.dumps(bal))
post("/api/v1/resources/relations", {"source_id": "x", "target_id": "y", "relation_type": "z"})
core.put("/api/v1/resources", json={"resource_id": res_id, "resource_type": "broker_task", "owner_service": "ai_broker", "revision": 2, "data": {"status": "completed"}})
core.put("/api/v1/resources", json={"resource_id": oid, "resource_type": "objective", "owner_service": "ai_os_core"})
r = post("/api/v1/resources/relations", {"source_id": oid, "target_id": res_id, "relation_type": "fulfilled_by"})
step("grafo: objetivo -> tarea del broker", r.status_code == 201)
b = core.put("/api/v1/identity-bindings", json={"global_id": op_id, "native_id": task_id, "source_system": "ai_broker"})
step("identity binding operación -> task_id nativo", b.status_code == 200 and b.json()["native_id"] == task_id)
core.patch(f"/api/v1/objectives/{oid}/status", json={"status": "completed", "principal_id": "e2e"})

# 11. Repetir la petición al broker con la misma clave: no crea otra tarea
again = broker.post("/api/v1/tasks", json=broker_body)
step("broker: misma idempotency_key devuelve la misma tarea", again.json().get("task_id") == task_id, str(again.status_code))

# 12. Agora: proyección de solo lectura del tablero
board = agora.get("/api/v1/board").json()
profiles = agora.get("/api/v1/profiles").json()
print("      tablero:", json.dumps(board)[:300])
counts = board.get("counts") or {k: len(v) for k, v in board.items() if isinstance(v, list)}
seq += 1
r = post("/api/v1/events/inbox", {"event_id": f"ev_agora_{run}", "producer_id": "agora_board", "stream_id": f"board_{run}",
                                  "stream_epoch": 1, "source_sequence": 1, "event_type": "full_state", "resource_id": "agora:board",
                                  "resource_type": "agora_board", "revision": int(time.time()), "payload": {"counts": counts,
                                  "profiles": len(profiles) if isinstance(profiles, list) else len(profiles.get("items", profiles))},
                                  "state_digest": hashlib.sha256(json.dumps(board, sort_keys=True).encode()).hexdigest()})
step("snapshot del tablero de Agora proyectado en el Core", r.json()["accepted_in_canonical_projection"])
step("estado canónico del tablero consultable", core.get("/api/v1/events/canonical/agora:board").status_code == 200)

goal_audit = core.get(f"/api/v1/goals/{gid}/audit").json()
step("auditoría de la meta", len(goal_audit) >= 1)
print(f"\nE2E completo: {ok_count} comprobaciones OK. run={run} task_id={task_id}")
