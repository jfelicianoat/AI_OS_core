"""Monitor visual (0.3.0): pasos de flujo, decisiones y recibos anotados, stream y página.
Comentarios en español.
"""

import json
import os
import threading
import unittest
import uuid

from fastapi.testclient import TestClient
from ai_os_core.app import create_app


def _uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


class TestFlowsMonitor(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(create_app(), raise_server_exceptions=False)
        cls.client.__enter__()

    @classmethod
    def tearDownClass(cls):
        cls.client.__exit__(None, None, None)

    def _hop(self, flow, src="chatygpt", dst="athena", kind="request", **extra):
        body = {"flow_id": flow, "source_system": src, "target_system": dst, "kind": kind, **extra}
        return self.client.post("/api/v1/flows/hops", json=body)

    def test_hop_is_stored_and_listed_in_order(self):
        flow = _uid("f")
        self.assertEqual(self._hop(flow).status_code, 201)
        self.assertEqual(self._hop(flow, kind="response", details={"latency_ms": 900}).status_code, 201)
        steps = self.client.get(f"/api/v1/flows/{flow}").json()["steps"]
        self.assertEqual([s["kind"] for s in steps], ["request", "response"])
        # Repetir el mismo salto (una app que sondea un estado terminal) no lo duplica
        self.assertEqual(self._hop(flow, kind="response", details={"latency_ms": 950}).status_code, 201)
        self.assertEqual(len(self.client.get(f"/api/v1/flows/{flow}").json()["steps"]), 2)
        self.assertEqual(steps[1]["details"], {"latency_ms": 900})
        tail = self.client.get("/api/v1/flows/events", params={"after": steps[0]["id"] - 1}).json()
        self.assertEqual([s["id"] for s in tail[:2]], [s["id"] for s in steps])

    def test_hop_validation(self):
        self.assertEqual(self._hop(_uid("f"), kind="teleport").status_code, 422)
        self.assertEqual(self._hop("con espacios").status_code, 422)
        # Sólo metadatos: un cuerpo grande (p. ej. el texto de la petición) se rechaza
        self.assertEqual(self._hop(_uid("f"), details={"prompt": "x" * 5000}).status_code, 422)
        self.assertEqual(self.client.get("/api/v1/flows/no_existe_nunca").status_code, 404)

    def test_policy_decision_joins_the_flow_of_the_request(self):
        scope = _uid("app") + ":broker"
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": _uid("k"), "scope": scope,
                                                   "decision_if_matched": "ALLOW", "unconditional": True})
        flow = _uid("f")
        d = self.client.post("/api/v1/policies/evaluate", json={
            "scope": scope, "context": {"data_classification": "internal", "flow_id": flow}}).json()
        step = self.client.get(f"/api/v1/flows/{flow}").json()["steps"][0]
        self.assertEqual(step["kind"], "decision")
        self.assertEqual(step["source"], scope.split(":")[0])  # sin principal declarado: el prefijo del ámbito
        self.assertEqual(step["details"]["authorization"], "ALLOW")
        self.assertEqual(step["details"]["trace_id"], d["trace_id"])
        self.assertEqual(step["details"]["data_classification"], "internal")
        # Sin flow_id la decisión abre su propio flujo con el trace_id
        d2 = self.client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {}}).json()
        self.assertEqual(self.client.get(f"/api/v1/flows/{d2['trace_id']}").status_code, 200)
        # Sin políticas no hay trace_id: aun así queda anotada (y la respuesta no cambia)
        r = self.client.post("/api/v1/policies/evaluate", json={"scope": _uid("vacio") + ":broker", "context": {"flow_id": flow}})
        self.assertEqual(r.json()["authorization"], "DENY")
        self.assertEqual(len(self.client.get(f"/api/v1/flows/{flow}").json()["steps"]), 2)

    def test_receipt_joins_the_flow_and_rejected_receipts_do_not(self):
        flow, op = _uid("f"), _uid("op")
        body = {"operation_id": op, "receiver_service": "ai_broker", "status": "succeeded", "evidence": {"flow_id": flow}}
        self.assertEqual(self.client.post("/api/v1/operations/receipts", json=body).status_code, 201)
        # Un recibo que retrocede lo rechaza Core (409) y no aparece en el monitor
        back = {**body, "status": "accepted"}
        self.assertEqual(self.client.post("/api/v1/operations/receipts", json=back).status_code, 409)
        steps = self.client.get(f"/api/v1/flows/{flow}").json()["steps"]
        self.assertEqual([(s["kind"], s["details"]["status"]) for s in steps], [("receipt", "succeeded")])

    def test_polling_does_not_flood_the_monitor(self):
        """El runner de Agora repite la consulta por cada tarjeta pendiente en cada vuelta."""
        scope, flow = _uid("sondeo") + ":broker", _uid("f")
        deny = {"policy_id": _uid("p"), "policy_key": _uid("k"), "scope": scope, "decision_if_matched": "DENY",
                "conditions": [{"field": "data_classification", "operator": "in", "value": ["restricted"]}]}
        self.client.post("/api/v1/policies", json=deny)
        self.client.post("/api/v1/policies", json={"policy_id": _uid("p"), "policy_key": _uid("k"), "scope": scope,
                                                   "decision_if_matched": "ALLOW", "unconditional": True})
        ask = lambda dc: self.client.post("/api/v1/policies/evaluate", json={
            "scope": scope, "context": {"data_classification": dc, "flow_id": flow}})
        for _ in range(3):
            ask("restricted")
        self.assertEqual(len(self.client.get(f"/api/v1/flows/{flow}").json()["steps"]), 1)
        ask("internal")  # la decisión cambia: eso sí se ve
        steps = self.client.get(f"/api/v1/flows/{flow}").json()["steps"]
        self.assertEqual([s["details"]["authorization"] for s in steps], ["DENY", "ALLOW"])

    def test_apps_marks_unregistered_participants(self):
        newcomer = _uid("nueva")
        self._hop(_uid("f"), src=newcomer, dst="ai_broker")
        apps = {a["app"]: a["known"] for a in self.client.get("/api/v1/flows/apps").json()}
        self.assertFalse(apps[newcomer])
        self.assertTrue(apps["ai_broker"])

    def test_monitor_page_and_assets_are_public_but_data_is_not(self):
        os.environ["AI_OS_API_TOKENS"] = "chatygpt=tok-chaty-mon"
        try:
            with TestClient(create_app(), raise_server_exceptions=False) as c:
                page = c.get("/monitor")
                self.assertEqual(page.status_code, 200)
                self.assertIn("text/html", page.headers["content-type"])
                self.assertEqual(c.get("/monitor/iconos/core.svg").status_code, 200)
                self.assertEqual(c.get("/monitor/fondo.jpg").status_code, 200)
                self.assertEqual(c.get("/monitor/..%2F..%2Fapp.py").status_code, 404)
                self.assertEqual(c.get("/api/v1/flows/events").status_code, 401)
                auth = {"Authorization": "Bearer tok-chaty-mon"}
                self.assertEqual(c.get("/api/v1/flows/events", headers=auth).status_code, 200)
                # El token de una app no puede informar saltos en nombre de otra
                bad = {"flow_id": _uid("f"), "source_system": "athena", "target_system": "ai_broker", "kind": "request"}
                self.assertEqual(c.post("/api/v1/flows/hops", json=bad, headers=auth).status_code, 403)
                ok = {**bad, "source_system": "chatygpt"}
                self.assertEqual(c.post("/api/v1/flows/hops", json=ok, headers=auth).status_code, 201)
        finally:
            del os.environ["AI_OS_API_TOKENS"]

    def test_api_calls_of_an_app_are_recorded_as_steps(self):
        app_id, flow = _uid("app"), _uid("f")
        who = {"X-Principal-Id": app_id}
        self.client.get("/api/v1/policies", headers={**who, "X-Flow-Id": flow})
        steps = self.client.get(f"/api/v1/flows/{flow}").json()["steps"]
        self.assertEqual([(s["kind"], s["source"], s["target"]) for s in steps], [("api", app_id, "core")])
        self.assertEqual({k: steps[0]["details"][k] for k in ("method", "path", "status")},
                         {"method": "GET", "path": "/api/v1/policies", "status": 200})
        self.assertGreater(steps[0]["details"]["bytes_out"], 0)
        # Sin X-Flow-Id: el flujo del día de esa app; un error también se anota
        self.client.get("/api/v1/certifications/m/c/v", headers=who)
        daily = [f for f in {e["flow_id"] for e in self.client.get("/api/v1/flows/events").json()} if f.startswith(f"api_{app_id}_")]
        self.assertEqual(len(daily), 1)
        self.assertEqual(self.client.get(f"/api/v1/flows/{daily[0]}").json()["steps"][0]["details"]["status"], 404)
        # Lo que ya tiene su propio paso, o no dice qué app es, no se duplica
        before = self.client.get("/api/v1/flows/events", params={"limit": 1}).json()[-1]["id"]
        self._hop(_uid("f"), src=app_id)
        self.client.get("/api/v1/flows/events", headers=who)
        self.client.get("/api/v1/policies")
        after = self.client.get("/api/v1/flows/events", params={"after": before}).json()
        self.assertEqual([s["kind"] for s in after], ["request"])

    def test_stream_delivers_new_steps(self):
        os.environ["AI_OS_MONITOR_POLL_S"] = "0.05"
        os.environ["AI_OS_MONITOR_MAX_S"] = "2"  # el cliente de pruebas no avisa al desconectar: que acabe solo
        try:
            last = self.client.get("/api/v1/flows/events", params={"limit": 1}).json()
            after = last[-1]["id"] if last else 0
            early, late = _uid("f"), _uid("f")
            self._hop(early)
            # El segundo paso llega con el stream ya abierto y varias vueltas de sondeo después
            threading.Timer(0.4, lambda: self._hop(late)).start()
            seen = []
            with self.client.stream("GET", "/api/v1/flows/stream", params={"after": after}) as r:
                self.assertEqual(r.status_code, 200)
                for line in r.iter_lines():
                    if line.startswith("data:"):
                        seen.append(json.loads(line[5:])["flow_id"])
                        if late in seen:
                            break
            self.assertIn(early, seen)
            self.assertIn(late, seen)
        finally:
            del os.environ["AI_OS_MONITOR_POLL_S"], os.environ["AI_OS_MONITOR_MAX_S"]


if __name__ == "__main__":
    unittest.main()
