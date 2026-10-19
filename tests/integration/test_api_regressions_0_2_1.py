"""Regresiones de la revisión 0.2.1 (2026-10-18), ejercitadas por HTTP.

Cada prueba reproduce un defecto encontrado sondeando la API: enteros que no caben
en SQLite daban 500, recibos de operación que retrocedían (un 'succeeded' volvía a
'retry_allowed'), reservas caducadas que seguían reteniendo saldo en las lecturas,
estados de salud ilegibles convertidos en 'healthy' y un planificador que aprobaba
con una decisión de política escrita por el propio cliente.
Comentarios en español.
"""

import time
import unittest
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient
from ai_os_core.app import create_app


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class TestApiRegressions021(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(), raise_server_exceptions=False)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def test_optional_api_token(self):
        import os
        os.environ["AI_OS_API_TOKEN"] = "secreto-de-prueba"
        try:
            with TestClient(create_app(), raise_server_exceptions=False) as c:
                self.assertEqual(c.get("/health").status_code, 200)
                self.assertEqual(c.get("/ready").status_code, 200)
                self.assertEqual(c.get("/api/v1/goals").status_code, 401)
                self.assertEqual(c.get("/api/v1/goals", headers={"Authorization": "Bearer otro"}).status_code, 401)
                # Sin token no se reserva la clave de idempotencia: el reintento autenticado entra
                h = {"Idempotency-Key": _uid("k")}
                body = {"title": "t", "description": "d"}
                self.assertEqual(c.post("/api/v1/goals", json=body, headers=h).status_code, 401)
                ok = c.post("/api/v1/goals", json=body, headers={**h, "Authorization": "Bearer secreto-de-prueba"})
                self.assertEqual(ok.status_code, 201, ok.text)
        finally:
            del os.environ["AI_OS_API_TOKEN"]
        # Sin la variable, la API sigue abierta como antes
        self.assertEqual(self.client.get("/api/v1/goals").status_code, 200)

    def test_per_app_tokens_fix_the_principal(self):
        import os
        os.environ["AI_OS_API_TOKENS"] = "chatygpt=tok-chaty-123;athena=tok-athena-456"
        try:
            with TestClient(create_app(), raise_server_exceptions=False) as c:
                chaty = {"Authorization": "Bearer tok-chaty-123"}
                self.assertEqual(c.get("/api/v1/goals").status_code, 401)
                self.assertEqual(c.get("/api/v1/goals", headers=chaty).status_code, 200)
                # Hacerse pasar por otra app: en la cabecera o en el cuerpo -> 403
                self.assertEqual(c.get("/api/v1/goals", headers={**chaty, "X-Principal-Id": "athena"}).status_code, 403)
                ev = {"scope": "s", "context": {}, "principal_id": "athena"}
                self.assertEqual(c.post("/api/v1/policies/evaluate", json=ev, headers=chaty).status_code, 403)
                self.assertEqual(c.post("/api/v1/policies/evaluate", json={**ev, "principal_id": "chatygpt"}, headers=chaty).status_code, 200)
                # La misma clave de idempotencia de dos apps son dos operaciones distintas
                h = {"Idempotency-Key": _uid("k")}
                a = c.post("/api/v1/goals", json={"title": "a", "description": "d"}, headers={**h, **chaty})
                b = c.post("/api/v1/goals", json={"title": "b", "description": "d"},
                           headers={**h, "Authorization": "Bearer tok-athena-456"})
                self.assertEqual((a.status_code, b.status_code), (201, 201), b.text)
                self.assertNotEqual(a.json()["id"], b.json()["id"])
                # Tampoco puede certificar ni producir eventos en nombre de otra
                cert = {"model_id": _uid("m"), "capability_id": "c", "version": "1",
                        "evaluation_verdict": "CERTIFIED", "is_applicable": True}
                self.assertEqual(c.post("/api/v1/certifications", json={**cert, "source_system": "model_drift"},
                                        headers=chaty).status_code, 403)
                self.assertEqual(c.post("/api/v1/certifications", json={**cert, "source_system": "chatygpt"},
                                        headers=chaty).status_code, 201)
                ev = {"event_id": _uid("ev"), "producer_id": "athena", "stream_id": "s", "epoch": 1,
                      "source_sequence": 1, "resource_id": "r", "event_type": "t", "payload": {}}
                self.assertEqual(c.post("/api/v1/events/inbox", json=ev, headers=chaty).status_code, 403)
        finally:
            del os.environ["AI_OS_API_TOKENS"]

    def test_token_limits_scopes_and_clearance(self):
        import os
        os.environ["AI_OS_API_TOKENS"] = "gti=tok-gti-1|planner:propose|INTERNAL;athena=tok-ath-2;lab=tok-lab-3|context:build|INTERNAL"
        try:
            with TestClient(create_app(), raise_server_exceptions=False) as c:
                gti = {"Authorization": "Bearer tok-gti-1"}
                pkg = {"classification_level": "INTERNAL", "principal_id": "gti"}
                # context:build no está entre sus scopes, ni explícito ni por defecto
                self.assertEqual(c.post("/api/v1/context/packages", json=pkg, headers=gti).status_code, 403)
                self.assertEqual(c.post("/api/v1/context/packages", json={**pkg, "principal_scopes": ["planner:propose"]},
                                        headers=gti).status_code, 403)  # 403 del propio Core: falta context:build
                gid = _uid("goal")
                c.post("/api/v1/goals", json={"title": "g", "description": "d", "goal_id": gid}, headers=gti)
                plan = {"goal_id": gid, "principal_id": "gti",
                        "tasks": [{"task_id": "t", "title": "t", "description": "d", "assigned_service": "x"}]}
                self.assertEqual(c.post("/api/v1/planner/proposals", json=plan, headers=gti).status_code, 201)
                over = c.post("/api/v1/planner/proposals", json={**plan, "principal_scopes": ["planner:propose", "admin"]}, headers=gti)
                self.assertEqual(over.status_code, 403, over.text)
                # Clearance por encima de lo concedido
                lab = {"Authorization": "Bearer tok-lab-3"}
                high = c.post("/api/v1/context/packages", json={"classification_level": "CONFIDENTIAL",
                              "principal_clearance": "CONFIDENTIAL", "principal_id": "lab"}, headers=lab)
                self.assertEqual(high.status_code, 403)
                self.assertIn("INTERNAL", high.json()["error"]["message"])
                self.assertEqual(c.post("/api/v1/context/packages", json={"classification_level": "INTERNAL",
                                        "principal_id": "lab"}, headers=lab).status_code, 201)
                ath = {"Authorization": "Bearer tok-ath-2"}
                self.assertEqual(c.post("/api/v1/context/packages", json={"classification_level": "CONFIDENTIAL",
                                        "principal_clearance": "CONFIDENTIAL", "principal_id": "athena"}, headers=ath).status_code, 201)
            os.environ["AI_OS_API_TOKENS"] = "gti=tok-gti-1||SECRETO"
            with self.assertRaises(ValueError):
                create_app()  # un nivel mal escrito no arranca abierto
        finally:
            del os.environ["AI_OS_API_TOKENS"]

    def test_integer_overflow_is_400_not_500(self):
        r = self.client.put("/api/v1/resources", json={"resource_id": _uid("r"), "resource_type": "t",
                                                       "owner_service": "s", "revision": 2 ** 63})
        self.assertEqual(r.status_code, 400, r.text)
        r = self.client.put("/api/v1/identity-bindings", json={"global_id": _uid("g"), "native_id": "n",
                                                               "source_system": "s", "adapter_revision": 2 ** 63})
        self.assertEqual(r.status_code, 400, r.text)

    def _receipt(self, op, status, receiver="broker"):
        return self.client.post("/api/v1/operations/receipts",
                                json={"operation_id": op, "receiver_service": receiver, "status": status})

    def test_receipts_only_move_forward(self):
        op = _uid("op")
        for st in ("accepted", "in_progress", "succeeded"):
            self.assertEqual(self._receipt(op, st).status_code, 201)
        self.assertEqual(self._receipt(op, "succeeded").status_code, 201)  # repetir el mismo es idempotente
        for st in ("not_seen", "accepted", "in_progress", "failed_terminal"):
            self.assertEqual(self._receipt(op, st).status_code, 409, st)
        st = self.client.post("/api/v1/operations/status", json={"operation_id": op, "target_service_id": "broker"}).json()
        self.assertEqual(st["recommended_action"], "reconstruct_state_no_resend")
        op2 = _uid("op")
        self._receipt(op2, "in_progress")
        self.assertEqual(self._receipt(op2, "accepted").status_code, 409)
        self.assertEqual(self._receipt(op2, "unknown").status_code, 201)

    def test_receipt_cannot_be_rewritten_by_other_receiver(self):
        op = _uid("op")
        self._receipt(op, "accepted", "broker")
        self.assertEqual(self._receipt(op, "succeeded", "intruso").status_code, 409)

    def test_expired_reservation_is_released_on_read(self):
        acc = _uid("acc")
        self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 10})
        soon = (datetime.now(timezone.utc) + timedelta(seconds=1)).isoformat()
        res = self.client.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 4, "expires_at": soon}).json()
        # Segunda cuenta: sólo se consulta la reserva, sin pasar antes por la cuenta
        acc2 = _uid("acc")
        self.client.post("/api/v1/budget/accounts", json={"account_id": acc2, "balance": 10})
        res2 = self.client.post("/api/v1/budget/reserve", json={"account_id": acc2, "amount": 4, "expires_at": soon}).json()
        self.assertEqual(self.client.get(f"/api/v1/budget/accounts/{acc}").json()["available"], 6.0)
        time.sleep(1.2)
        self.assertEqual(self.client.post("/api/v1/budget/consume", json={"reservation_id": res["reservation_id"]}).status_code, 409)
        account = self.client.get(f"/api/v1/budget/accounts/{acc}").json()
        self.assertEqual((account["reserved"], account["available"]), (0.0, 10.0))
        self.assertEqual(self.client.get(f"/api/v1/budget/reservations/{res['reservation_id']}").json()["status"], "expired")
        self.assertEqual(self.client.get(f"/api/v1/budget/reservations/{res2['reservation_id']}").json()["status"], "expired")

    def test_reservation_born_expired_is_rejected(self):
        acc = _uid("acc")
        self.client.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 10})
        r = self.client.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 1, "expires_at": "2000-01-01T00:00:00Z"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.client.get(f"/api/v1/budget/accounts/{acc}").json()["reserved"], 0.0)

    def test_service_registration_validation(self):
        base = {"name": "n", "base_url": "http://127.0.0.1:9"}
        self.assertEqual(self.client.post("/api/v1/services", json={**base, "service_id": _uid("s"), "health_status": "caido"}).status_code, 400)
        self.assertEqual(self.client.post("/api/v1/services", json={**base, "service_id": ""}).status_code, 422)
        ok = self.client.post("/api/v1/services", json={**base, "service_id": _uid("s"), "health_status": "down"})
        self.assertEqual(ok.json()["health_status"], "down")

    def _event(self, stream, eid, seq, rev, status, epoch=1, res=None):
        return self.client.post("/api/v1/events/inbox", json={
            "event_id": eid, "producer_id": "p", "stream_id": stream, "stream_epoch": epoch, "source_sequence": seq,
            "event_type": "full_state", "resource_id": res or stream, "resource_type": "t", "revision": rev,
            "payload": {"status": status}, "state_digest": status})

    def test_gap_is_resumed_when_missing_event_arrives(self):
        s = _uid("stream")
        self._event(s, f"{s}_1", 1, 1, "a")
        held = self._event(s, f"{s}_3", 3, 3, "c").json()
        self.assertTrue(held["quarantine"])
        # Antes el evento retenido contaba como procesado: seq 4 entraba y seq 3 se perdía
        early = self._event(s, f"{s}_4", 4, 4, "d").json()
        self.assertTrue(early["quarantine"], early)
        self.assertEqual(self.client.get(f"/api/v1/events/canonical/{s}").json()["revision"], 1)
        self._event(s, f"{s}_2", 2, 2, "b")
        self.assertEqual(self.client.get(f"/api/v1/events/canonical/{s}").json()["revision"], 4)
        gaps = [g for g in self.client.get("/api/v1/events/gaps").json() if g["stream_id"] == s]
        self.assertEqual(gaps, [])
        quarantined = [e["event_id"] for e in self.client.get("/api/v1/events/quarantine?limit=100").json()["items"]]
        self.assertNotIn(f"{s}_3", quarantined)
        self.assertEqual(self._event(s, f"{s}_5", 5, 5, "e").json()["quarantine"], False)

    def test_previous_epoch_is_audit_only(self):
        s = _uid("stream")
        self._event(s, f"{s}_e1", 1, 1, "a", epoch=1)
        self._event(s, f"{s}_e2", 1, 2, "b", epoch=2)
        late = self._event(s, f"{s}_late", 2, 9, "viejo", epoch=1).json()
        self.assertFalse(late["accepted_in_canonical_projection"])
        self.assertIn("STALE_EPOCH", late["reason"])
        self.assertEqual(self.client.get(f"/api/v1/events/canonical/{s}").json()["payload"]["status"], "b")

    def test_event_id_reused_with_other_content_is_conflict(self):
        s = _uid("stream")
        self._event(s, f"{s}_1", 1, 1, "a")
        self.assertTrue(self._event(s, f"{s}_1", 1, 1, "a").json()["duplicate"])
        self.assertEqual(self._event(s, f"{s}_1", 1, 1, "manipulado").status_code, 409)

    def test_sequence_must_be_positive_and_errors_share_envelope(self):
        r = self._event(_uid("stream"), _uid("e"), 0, 1, "a")
        self.assertEqual(r.status_code, 422)
        self.assertIn("source_sequence", r.json()["error"]["message"])
        self.assertIsInstance(r.json()["detail"], list)

    def test_certification_owned_by_its_source_system(self):
        base = {"model_id": _uid("m"), "capability_id": "llm.task", "version": "1", "evaluation_verdict": "CERTIFIED",
                "is_applicable": True}
        self.assertEqual(self.client.post("/api/v1/certifications", json={**base, "source_system": "model_drift", "revision": 1}).status_code, 201)
        r = self.client.post("/api/v1/certifications", json={**base, "source_system": "intruso", "revision": 5})
        self.assertEqual(r.status_code, 409)
        got = self.client.get(f"/api/v1/certifications/{base['model_id']}/llm.task/1").json()
        self.assertEqual((got["source_system"], got["revision"]), ("model_drift", 1))

    def test_certification_of_broker_model_key_with_slashes(self):
        # Los modelos del Broker son "proveedor/despliegue/modelo": la consulta por ruta debe encontrarlos
        model = f"ollama/local/{_uid('m')}:latest"
        self.client.post("/api/v1/certifications", json={"model_id": model, "capability_id": "suite:facturacion", "version": "1",
                                                         "source_system": "model_drift", "evaluation_verdict": "CERTIFIED",
                                                         "is_applicable": True})
        r = self.client.get(f"/api/v1/certifications/{model}/suite:facturacion/1")
        self.assertEqual(r.status_code, 200, r.text)
        self.assertEqual(r.json()["model_id"], model)

    def _proposal(self, policy_decision):
        gid = _uid("goal")
        self.client.post("/api/v1/goals", json={"title": "g", "description": "d", "goal_id": gid})
        return self.client.post("/api/v1/planner/proposals", json={
            "goal_id": gid, "requested_autonomy": "A3", "policy_decision": policy_decision,
            "tasks": [{"task_id": "t1", "title": "t", "description": "d", "assigned_service": "ai_broker"}]})

    def _decide(self, pid):
        return self.client.post(f"/api/v1/planner/proposals/{pid}/decision", json={"applicable_ceilings": ["A3"]}).json()

    def test_planner_only_trusts_core_policy_decisions(self):
        forged = self._proposal({"authorization": "ALLOW", "executable": True})
        self.assertEqual(forged.status_code, 400, forged.text)
        bad_trace = self._proposal({"authorization": "ALLOW", "executable": True, "trace_id": "trace_inventado"})
        self.assertEqual(bad_trace.status_code, 400)
        empty = self._proposal({})
        self.assertEqual(empty.status_code, 201)
        self.assertFalse(self._decide(empty.json()["proposal_id"])["approved_for_dispatch"])

        scope = _uid("scope")
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": "k", "scope": scope,
                         "decision_if_matched": "ALLOW", "unconditional": True})
        dec = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {}}).json()
        self.assertTrue(dec["trace_id"].startswith("trace_"))
        # Una traza real cuyo resultado se altera tampoco cuela
        tampered = self._proposal({**dec, "executable": not dec["executable"]})
        self.assertEqual(tampered.status_code, 400)
        real = self._proposal(dec)
        self.assertEqual(real.status_code, 201, real.text)
        self.assertTrue(self._decide(real.json()["proposal_id"])["approved_for_dispatch"])


if __name__ == "__main__":
    unittest.main()
