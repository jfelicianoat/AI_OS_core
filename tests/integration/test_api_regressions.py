"""Regresiones de la revisión 0.2.0 ejercitadas por HTTP, como las usa un cliente.

Cada prueba reproduce un defecto encontrado contra la API real: carreras de
C07/C09/C01 con peticiones simultáneas, duplicados que daban 500, decisiones que
fallaban en abierto (fail-open) y huecos del validador SSRF.
Comentarios en español.
"""

import threading
import time
import unittest
import uuid

from fastapi.testclient import TestClient
from ai_os_core.app import create_app


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def _concurrent(n: int, fn) -> list[int]:
    """Lanza n peticiones a la vez y devuelve sus códigos HTTP ordenados."""
    codes: list[int] = []
    barrier = threading.Barrier(n)

    def worker(i: int) -> None:
        barrier.wait()
        codes.append(fn(i).status_code)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(n)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return sorted(codes)


class TestApiRegressions(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(), raise_server_exceptions=False)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    # --- Carreras reales ---------------------------------------------------

    def test_c09_concurrent_reservations_never_overdraw(self):
        acc = _uid("acc")
        self.assertEqual(self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 100}).status_code, 201)
        codes = _concurrent(10, lambda i: self.client.post(
            "/api/v1/budget/reserve", json={"account_id": acc, "amount": 80, "reservation_id": f"{acc}_{i}"}))
        self.assertEqual(codes.count(201), 1, codes)
        self.assertEqual(codes.count(409), 9, codes)
        account = self.client.get(f"/api/v1/budget/accounts/{acc}").json()
        self.assertEqual(account["reserved"], 80.0)

    def test_c07_last_use_committed_once_under_race(self):
        auth = _uid("auth")
        self.client.post("/api/v1/approvals", json={"authorization_id": auth, "scope": "s", "max_uses": 1})
        codes = _concurrent(10, lambda i: self.client.post("/api/v1/approvals/use", json={
            "use_id": f"{auth}_u{i}", "authorization_id": auth, "operation_id": f"op{i}", "operation_digest": "d"}))
        self.assertEqual(codes.count(200), 1, codes)
        state = self.client.get(f"/api/v1/approvals/{auth}/status").json()
        self.assertEqual(state["used_count"], 1)

    def test_c01_concurrent_same_key_creates_one_goal(self):
        key = _uid("idem")
        title = _uid("meta")
        codes = _concurrent(8, lambda i: self.client.post(
            "/api/v1/goals", json={"title": title, "description": "d"}, headers={"X-Idempotency-Key": key}))
        # Todas terminan bien (201 o repetición) o se les pide reintentar (409 in-progress)
        self.assertTrue(set(codes) <= {201, 409}, codes)
        goals = self.client.get("/api/v1/goals?limit=100").json()["items"]
        offset = 100
        while True:
            page = self.client.get(f"/api/v1/goals?limit=100&offset={offset}").json()["items"]
            if not page:
                break
            goals += page
            offset += 100
        self.assertEqual(sum(1 for g in goals if g["title"] == title), 1)

    # --- Idempotencia HTTP -------------------------------------------------

    def test_c01_conflict_is_409_and_namespaced_by_principal(self):
        key = _uid("idem")
        first = self.client.post("/api/v1/goals", json={"title": "a", "description": "d"},
                                 headers={"X-Idempotency-Key": key, "X-Principal-Id": "alice"})
        replay = self.client.post("/api/v1/goals", json={"title": "a", "description": "d"},
                                  headers={"X-Idempotency-Key": key, "X-Principal-Id": "alice"})
        self.assertEqual(replay.headers.get("X-Idempotent-Replay"), "true")
        self.assertEqual(first.json()["id"], replay.json()["id"])

        conflict = self.client.post("/api/v1/goals", json={"title": "b", "description": "d"},
                                    headers={"X-Idempotency-Key": key, "X-Principal-Id": "alice"})
        self.assertEqual(conflict.status_code, 409)
        self.assertEqual(conflict.json()["error"]["type"], "IdempotencyConflict")

        # Otro principal con la misma clave no recibe la respuesta de alice
        other = self.client.post("/api/v1/goals", json={"title": "a", "description": "d"},
                                 headers={"X-Idempotency-Key": key, "X-Principal-Id": "bob"})
        self.assertEqual(other.status_code, 201)
        self.assertNotEqual(other.json()["id"], first.json()["id"])

    # --- Duplicados y referencias -----------------------------------------

    def test_duplicates_are_409_not_500(self):
        auth = _uid("auth")
        self.client.post("/api/v1/approvals", json={"authorization_id": auth, "scope": "s"})
        self.assertEqual(self.client.post("/api/v1/approvals", json={"authorization_id": auth, "scope": "s"}).status_code, 409)

        gid = _uid("goal")
        self.client.post("/api/v1/goals", json={"title": "orig", "description": "d", "goal_id": gid})
        self.client.patch(f"/api/v1/goals/{gid}/status", json={"status": "completed"})
        self.assertEqual(self.client.post("/api/v1/goals", json={"title": "x", "description": "d", "goal_id": gid}).status_code, 409)
        goal = self.client.get(f"/api/v1/goals/{gid}").json()
        self.assertEqual((goal["title"], goal["status"], goal["revision"]), ("orig", "completed", 2))

        self.assertEqual(self.client.post("/api/v1/goals", json={"title": "x", "description": "d", "parent_goal_id": "nope"}).status_code, 400)

    def test_event_redelivery_is_acknowledged_and_slot_conflict_is_409(self):
        stream = _uid("stream")
        ev = dict(event_id=_uid("ev"), producer_id="p", stream_id=stream, stream_epoch=1, source_sequence=1,
                  event_type="full_state", resource_id=_uid("res"), resource_type="doc", revision=1,
                  payload={"a": 1}, state_digest="d1")
        self.assertFalse(self.client.post("/api/v1/events/inbox", json=ev).json()["duplicate"])
        again = self.client.post("/api/v1/events/inbox", json=ev)
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.json()["duplicate"])
        self.assertEqual(self.client.post("/api/v1/events/inbox", json={**ev, "event_id": _uid("ev")}).status_code, 409)

    def test_gap_event_is_listed_in_quarantine(self):
        stream = _uid("stream")
        base = dict(producer_id="p", stream_id=stream, stream_epoch=1, event_type="delta",
                    resource_id=_uid("res"), resource_type="doc", revision=1, payload={})
        self.client.post("/api/v1/events/inbox", json={**base, "event_id": _uid("ev"), "source_sequence": 1})
        gap_id = _uid("ev")
        r = self.client.post("/api/v1/events/inbox", json={**base, "event_id": gap_id, "source_sequence": 4})
        self.assertTrue(r.json()["quarantine"])
        ids = [e["event_id"] for e in self.client.get("/api/v1/events/quarantine?limit=100").json()["items"]]
        self.assertIn(gap_id, ids)

    # --- Presupuesto ---------------------------------------------------------

    def test_budget_account_lifecycle(self):
        acc = _uid("acc")
        self.assertEqual(self.client.get(f"/api/v1/budget/accounts/{acc}").status_code, 404)
        self.assertEqual(self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 50}).status_code, 201)
        self.assertEqual(self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 50}).status_code, 409)
        rid = _uid("res")
        self.client.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 20, "reservation_id": rid})
        self.assertEqual(self.client.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 1, "reservation_id": rid}).status_code, 409)
        self.assertEqual(self.client.post("/api/v1/budget/consume", json={"reservation_id": rid}).status_code, 200)
        self.assertEqual(self.client.post("/api/v1/budget/consume", json={"reservation_id": rid}).status_code, 409)
        self.assertEqual(self.client.post("/api/v1/budget/release", json={"reservation_id": rid}).status_code, 409)
        self.assertEqual(self.client.post("/api/v1/budget/release", json={"reservation_id": "nada"}).status_code, 404)
        self.assertEqual(self.client.get(f"/api/v1/budget/accounts/{acc}").json()["balance"], 30.0)

    def test_expired_reservation_returns_to_available(self):
        acc = _uid("acc")
        self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 100})
        # Desde 0.2.1 no se admite una reserva que nace caducada: caduca en ~2 s
        soon = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(time.time() + 2))
        self.assertEqual(self.client.post("/api/v1/budget/reserve", json={
            "account_id": acc, "amount": 90, "reservation_id": f"{acc}_old", "expires_at": soon}).status_code, 201)
        time.sleep(2.1)
        r = self.client.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 90})
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.client.get(f"/api/v1/budget/reservations/{acc}_old").json()["status"], "expired")

    # --- Aprobaciones --------------------------------------------------------

    def test_approval_expiry_uses_instants_and_rejects_garbage(self):
        self.assertEqual(self.client.post("/api/v1/approvals", json={
            "authorization_id": _uid("a"), "scope": "s", "expires_at": "mañana"}).status_code, 400)
        self.assertEqual(self.client.post("/api/v1/approvals", json={
            "authorization_id": _uid("a"), "scope": "s", "max_uses": 0}).status_code, 422)
        # 01:00+02:00 de hoy ya pasó en UTC aunque como texto pareciera futuro respecto a "00:30Z"
        past = _uid("a")
        self.client.post("/api/v1/approvals", json={"authorization_id": past, "scope": "s", "expires_at": "2001-01-01T01:00:00+02:00"})
        self.assertEqual(self.client.get(f"/api/v1/approvals/{past}/status").json()["status"], "expired")

    def test_exact_action_approval_checks_digest_and_revoke(self):
        auth = _uid("auth")
        self.client.post("/api/v1/approvals", json={"authorization_id": auth, "scope": "s", "max_uses": 3, "expected_digest": "abc"})
        bad = self.client.post("/api/v1/approvals/use", json={"use_id": _uid("u"), "authorization_id": auth, "operation_id": "o1", "operation_digest": "zzz"})
        self.assertEqual(bad.status_code, 403)
        ok = self.client.post("/api/v1/approvals/use", json={"use_id": _uid("u"), "authorization_id": auth, "operation_id": "o2", "operation_digest": "abc"})
        self.assertEqual(ok.status_code, 200)
        state = self.client.post(f"/api/v1/approvals/{auth}/revoke", json={"reason": "test"}).json()
        self.assertEqual(state["status"], "revoked")
        after = self.client.post("/api/v1/approvals/use", json={"use_id": _uid("u"), "authorization_id": auth, "operation_id": "o3", "operation_digest": "abc"})
        self.assertEqual(after.status_code, 403)
        self.assertEqual(self.client.post("/api/v1/approvals/nada/revoke", json={}).status_code, 404)

    # --- Certificaciones -----------------------------------------------------

    def test_certification_stale_revision_rejected(self):
        model = _uid("model")
        base = dict(model_id=model, capability_id="c", version="1", source_system="model_drift",
                    evaluation_verdict="CERTIFIED", is_applicable=True)
        self.client.post("/api/v1/certifications", json={**base, "revision": 5})
        stale = self.client.post("/api/v1/certifications", json={**base, "revision": 2, "evaluation_verdict": "REJECTED"})
        self.assertEqual(stale.status_code, 409)
        self.assertEqual(self.client.get(f"/api/v1/certifications/{model}/c/1").json()["revision"], 5)

    # --- Políticas -----------------------------------------------------------

    def test_policy_rejects_unknown_operator_and_mode(self):
        scope = _uid("scope")
        bad_op = self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "k", "scope": scope,
                                  "decision_if_matched": "ALLOW", "conditions": [{"field": "a", "operator": "magia", "value": 1}]})
        self.assertEqual(bad_op.status_code, 400)
        bad_mode = self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "k", "scope": scope,
                                    "decision_if_matched": "ALLOW", "condition_mode": "xor", "conditions": [{"field": "a", "operator": "exists"}]})
        self.assertEqual(bad_mode.status_code, 400)

    def test_policy_uncomparable_value_is_indeterminate_not_allow(self):
        scope = _uid("scope")
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "coste", "scope": scope,
                         "decision_if_matched": "DENY", "conditions": [{"field": "cost", "operator": "greater_than", "value": 10}]})
        decision = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {"cost": "caro"}}).json()
        self.assertEqual(decision["authorization"], "INDETERMINATE")
        self.assertIn("cost", decision["unknown_inputs"])
        self.assertFalse(decision["executable"])
        listed = self.client.get(f"/api/v1/policies?scope={scope}").json()
        self.assertEqual(len(listed), 1)

    def test_unknown_restrictive_policy_is_not_masked_by_allow(self):
        scope = _uid("scope")
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "coste", "scope": scope,
                         "decision_if_matched": "DENY", "conditions": [{"field": "estimated_cost", "operator": "greater_than", "value": 5}]})
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "base", "scope": scope,
                         "decision_if_matched": "ALLOW", "unconditional": True})
        decision = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {}}).json()
        self.assertEqual(decision["authorization"], "INDETERMINATE")
        self.assertFalse(decision["executable"])
        cheap = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {"estimated_cost": 1}}).json()
        self.assertEqual(cheap["authorization"], "ALLOW")

    # --- Planner -------------------------------------------------------------

    def _plan(self, policy_decision=None, autonomy="A4", approval=False):
        gid = _uid("goal")
        self.client.post("/api/v1/goals", json={"title": "g", "description": "d", "goal_id": gid})
        r = self.client.post("/api/v1/planner/proposals", json={
            "goal_id": gid, "requested_autonomy": autonomy, "policy_decision": policy_decision or {},
            "tasks": [{"task_id": "t1", "title": "t", "description": "d", "assigned_service": "agora",
                       "requires_human_approval": approval}]})
        self.assertEqual(r.status_code, 201, r.text)
        return r.json()["proposal_id"]

    def test_planner_invalid_ceiling_is_rejected(self):
        pid = self._plan()
        r = self.client.post(f"/api/v1/planner/proposals/{pid}/decision", json={"applicable_ceilings": ["A1x"]})
        self.assertEqual(r.status_code, 400)

    def test_planner_respects_policy_decision_and_a0(self):
        denied = self._plan({"authorization": "DENY", "executable": False})
        d = self.client.post(f"/api/v1/planner/proposals/{denied}/decision", json={"applicable_ceilings": ["A5"]}).json()
        self.assertFalse(d["approved_for_dispatch"])
        # Un ALLOW sólo vale si lo emitió el Core (0.2.1): se pide una evaluación real
        scope = _uid("plan_scope")
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "base", "scope": scope,
                         "decision_if_matched": "ALLOW", "unconditional": True})
        allow = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {}}).json()
        self.assertEqual(allow["authorization"], "ALLOW")
        manual = self._plan(allow)
        d = self.client.post(f"/api/v1/planner/proposals/{manual}/decision", json={"applicable_ceilings": ["A0"]}).json()
        self.assertFalse(d["approved_for_dispatch"])
        self.assertEqual(d["effective_autonomy"], "A0")
        allowed = self._plan(allow)
        d = self.client.post(f"/api/v1/planner/proposals/{allowed}/decision", json={"applicable_ceilings": ["A3"]}).json()
        self.assertTrue(d["approved_for_dispatch"])
        self.assertEqual(d["effective_autonomy"], "A3")

    def test_planner_requires_existing_goal(self):
        r = self.client.post("/api/v1/planner/proposals", json={"goal_id": "no-existe", "tasks": [
            {"task_id": "t", "title": "t", "description": "d", "assigned_service": "x"}]})
        self.assertEqual(r.status_code, 404)

    # --- SSRF ----------------------------------------------------------------

    def test_ssrf_blocks_link_local_mapped_unspecified_and_public(self):
        for url in ["http://169.254.1.1", "http://[::ffff:169.254.169.254]/", "http://0.0.0.0:80",
                    "http://8.8.8.8", "http://[fe80::1]/", "http://evil.example.com"]:
            r = self.client.post("/api/v1/services", json={"service_id": _uid("s"), "name": "n", "base_url": url})
            self.assertEqual(r.status_code, 400, url)
        for url in ["http://127.0.0.1:8765", "http://localhost:8000", "http://192.168.1.52:8765"]:
            r = self.client.post("/api/v1/services", json={"service_id": _uid("s"), "name": "n", "base_url": url})
            self.assertEqual(r.status_code, 201, url)

    # --- Grafo, identidad, restore y contexto --------------------------------

    def test_resource_graph_and_identity_binding_api(self):
        a, b = _uid("res"), _uid("res")
        self.assertEqual(self.client.put("/api/v1/resources", json={"resource_id": a, "resource_type": "task", "owner_service": "gestion_tareas", "revision": 2}).status_code, 200)
        self.client.put("/api/v1/resources", json={"resource_id": b, "resource_type": "job", "owner_service": "agora"})
        self.assertEqual(self.client.put("/api/v1/resources", json={"resource_id": a, "resource_type": "task", "owner_service": "intruso"}).status_code, 409)
        self.assertEqual(self.client.put("/api/v1/resources", json={"resource_id": a, "resource_type": "task", "owner_service": "gestion_tareas", "revision": 1}).status_code, 409)
        self.client.post("/api/v1/resources/relations", json={"source_id": a, "target_id": b, "relation_type": "executed_by"})
        node = self.client.get(f"/api/v1/resources/{a}").json()
        self.assertEqual(node["relations"][0]["target_id"], b)

        gid = _uid("global")
        self.client.put("/api/v1/identity-bindings", json={"global_id": gid, "native_id": "42", "source_system": "agora", "adapter_revision": 3})
        self.assertEqual(self.client.put("/api/v1/identity-bindings", json={"global_id": gid, "native_id": "43", "source_system": "agora", "adapter_revision": 2}).status_code, 409)
        self.assertEqual(self.client.get(f"/api/v1/identity-bindings/{gid}/agora").json()["native_id"], "42")

    def test_restore_receipt_drives_recommended_action(self):
        op = _uid("op")
        q = self.client.post("/api/v1/operations/status", json={"operation_id": op, "target_service_id": "agora"}).json()
        self.assertEqual(q["recommended_action"], "retry_allowed")
        self.client.post("/api/v1/operations/receipts", json={"operation_id": op, "receiver_service": "agora", "status": "succeeded"})
        q = self.client.post("/api/v1/operations/status", json={"operation_id": op, "target_service_id": "agora"}).json()
        self.assertEqual(q["recommended_action"], "reconstruct_state_no_resend")
        self.assertEqual(self.client.post("/api/v1/operations/receipts", json={"operation_id": op, "receiver_service": "agora", "status": "rarísimo"}).status_code, 400)

    def test_context_invalid_clearance_is_rejected(self):
        r = self.client.post("/api/v1/context/packages", json={"classification_level": "PUBLIC", "principal_clearance": "XX"})
        self.assertEqual(r.status_code, 400)

    def test_timestamps_are_per_instance(self):
        a = self.client.post("/api/v1/approvals", json={"authorization_id": _uid("a"), "scope": "s"}).json()
        time.sleep(0.01)
        b = self.client.post("/api/v1/approvals", json={"authorization_id": _uid("a"), "scope": "s"}).json()
        self.assertNotEqual(a["created_at"], b["created_at"])

    def test_error_envelope_is_uniform(self):
        r = self.client.get("/api/v1/goals/no-existe")
        self.assertEqual(r.status_code, 404)
        self.assertIn("error", r.json())
        self.assertIn("detail", r.json())


if __name__ == "__main__":
    unittest.main()
