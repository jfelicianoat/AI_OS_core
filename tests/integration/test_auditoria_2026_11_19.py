"""Regresiones de la auditoría del 19-nov-2026 (docs/Auditoria 20261119/REGISTRO.md).

Cada test falla con el código 0.4.4 y pasa con la corrección.
"""

import runpy, pathlib; runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] / "__init__.py"))  # aislamiento (ver tests/__init__.py), se lance como se lance
import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi.testclient import TestClient

from ai_os_core.api.dependencies import get_db_manager
from ai_os_core.api.routes import credentials
from ai_os_core.app import create_app
from ai_os_core.infrastructure.db.repositories.flows_repo import FlowsRepository

DIRECTOR = {"Authorization": "Bearer tok-director"}
CHAT = {"Authorization": "Bearer tok-chat"}


def _uid(prefijo):
    return f"{prefijo}_{uuid.uuid4().hex[:10]}"


def _pol(pid, key, scope, decision="ALLOW", revision=1, **extra):
    return {"policy_id": pid, "policy_key": key, "scope": scope, "decision_if_matched": decision,
            "unconditional": True, "revision": revision, **extra}


class _ConTokens(unittest.TestCase):
    """Core con token de director y tokens por app, sin tocar el perfil."""

    VARS = ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS", "AI_OS_AUTO_TOKENS", "AI_OS_CONNECT_DIR", "AI_OS_APPS_FILE")

    def setUp(self):
        self._env = {k: os.environ.get(k) for k in self.VARS}
        os.environ.update(AI_OS_AUTO_TOKENS="false", AI_OS_API_TOKEN="tok-director",
                          AI_OS_API_TOKENS="chatygpt=tok-chat;gestion_tareas=tok-gti")
        credentials.reset_for_tests()
        self.c = TestClient(create_app(), raise_server_exceptions=False)
        self.c.__enter__()

    def tearDown(self):
        self.c.__exit__(None, None, None)
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        credentials.reset_for_tests()


class TestA01AdministracionSoloDirector(_ConTokens):

    def test_una_app_no_puede_dejar_sin_broker_a_las_demas(self):
        scope = _uid("gti") + ":broker"
        self.assertEqual(self.c.post("/api/v1/policies", json=_pol(_uid("p"), "base", scope), headers=DIRECTOR).status_code, 201)
        r = self.c.post("/api/v1/policies", json=_pol(_uid("p"), _uid("k"), "*", "DENY"), headers=CHAT)
        self.assertEqual(r.status_code, 403, r.text)
        dec = self.c.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {}}, headers=DIRECTOR).json()
        self.assertEqual(dec["authorization"], "ALLOW")

    def test_una_app_no_se_concede_aprobaciones_ni_registra_ni_crea_saldo(self):
        auth = _uid("a")
        for ruta, cuerpo in (
            ("/api/v1/approvals", {"authorization_id": auth, "scope": "x", "granted_by": "human"}),
            ("/api/v1/services", {"service_id": _uid("s"), "name": "s", "base_url": "http://127.0.0.1:1"}),
            ("/api/v1/capabilities", {"capability_id": _uid("c"), "name": "c", "description": "d", "provider_service_id": "s"}),
            ("/api/v1/budget/accounts", {"account_id": _uid("acc"), "balance": 1e9}),
        ):
            self.assertEqual(self.c.post(ruta, json=cuerpo, headers=CHAT).status_code, 403, ruta)
        self.assertEqual(self.c.post("/api/v1/approvals", json={"authorization_id": auth, "scope": "x"}, headers=DIRECTOR).status_code, 201)
        self.assertEqual(self.c.post(f"/api/v1/approvals/{auth}/revoke", json={}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.get(f"/api/v1/approvals/{auth}/status", headers=CHAT).json()["status"], "active")

    def test_las_apps_siguen_haciendo_lo_suyo(self):
        """Lo que usan las apps de verdad (evaluar, recibos, saltos) no cambia."""
        r = self.c.post("/api/v1/policies/evaluate", json={"scope": "chatygpt:broker", "context": {}, "principal_id": "chatygpt"}, headers=CHAT)
        self.assertEqual(r.status_code, 200)
        r = self.c.post("/api/v1/operations/receipts", json={"operation_id": _uid("op"), "receiver_service": "ai_broker", "status": "accepted"}, headers=CHAT)
        self.assertEqual(r.status_code, 201)
        r = self.c.post("/api/v1/flows/hops", json={"flow_id": _uid("f"), "source_system": "chatygpt", "target_system": "ai_broker", "kind": "request"}, headers=CHAT)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(self.c.get("/api/v1/services", headers=CHAT).status_code, 200)


class TestA02A04Politicas(_ConTokens):

    def _post(self, body):
        return self.c.post("/api/v1/policies", json=body, headers=DIRECTOR)

    def test_a02_un_policy_id_no_cambia_de_ambito_en_silencio(self):
        pid, a, b = _uid("p"), _uid("s"), _uid("s")
        self.assertEqual(self._post(_pol(pid, "k", a)).status_code, 201)
        r = self._post(_pol(pid, "k", b))
        self.assertEqual(r.status_code, 409, r.text)
        self.assertEqual([p["scope"] for p in self.c.get("/api/v1/policies", headers=DIRECTOR).json() if p["policy_id"] == pid], [a])

    def test_a03_la_revision_no_retrocede_y_rehacerla_es_200(self):
        pid, s = _uid("p"), _uid("s")
        self._post(_pol(pid, "k", s, "DENY", revision=5))
        self.assertEqual(self._post(_pol(pid, "k", s, "ALLOW", revision=2)).status_code, 409)
        r = self._post(_pol(pid, "k", s, "DENY", revision=5, enabled=False))  # lo que hacen los guiones de verificación
        self.assertEqual((r.status_code, r.json()["status"]), (200, "updated"))
        pol = next(p for p in self.c.get("/api/v1/policies", headers=DIRECTOR).json() if p["policy_id"] == pid)
        self.assertEqual((pol["revision"], pol["decision_if_matched"], pol["enabled"]), (5, "DENY", False))

    def test_a04_una_sola_politica_habilitada_por_clave_y_ambito(self):
        s = _uid("s")
        primera, segunda = _uid("p"), _uid("p")
        self._post(_pol(primera, "k", s, "ALLOW"))
        self.assertEqual(self._post(_pol(segunda, "k", s, "DENY")).status_code, 409)
        # Deshabilitada la primera, la segunda ya puede entrar
        self._post(_pol(primera, "k", s, "ALLOW", enabled=False))
        self.assertEqual(self._post(_pol(segunda, "k", s, "DENY")).status_code, 201)
        dec = self.c.post("/api/v1/policies/evaluate", json={"scope": s, "context": {}}, headers=DIRECTOR).json()
        self.assertEqual(dec["matched_policy_refs"], [segunda])


class TestO2OperacionesSobreLoDeOtraApp(_ConTokens):
    """Arbitraje O-2: con su token, una app no gasta, agota ni reescribe lo de otra."""

    def test_metas_y_presupuesto_son_del_director(self):
        acc = _uid("acc")
        self.assertEqual(self.c.post("/api/v1/budget/accounts", json={"account_id": acc, "balance": 10}, headers=DIRECTOR).status_code, 201)
        self.assertEqual(self.c.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 10}, headers=CHAT).status_code, 403)
        res = self.c.post("/api/v1/budget/reserve", json={"account_id": acc, "amount": 4}, headers=DIRECTOR).json()
        for ruta in ("consume", "release"):
            self.assertEqual(self.c.post(f"/api/v1/budget/{ruta}", json={"reservation_id": res["reservation_id"]}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.get(f"/api/v1/budget/accounts/{acc}", headers=CHAT).json()["available"], 6)
        goal = self.c.post("/api/v1/goals", json={"title": "t", "description": "d"}, headers=DIRECTOR).json()["id"]
        self.assertEqual(self.c.post("/api/v1/goals", json={"title": "t", "description": "d"}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.patch(f"/api/v1/goals/{goal}/status", json={"status": "cancelled"}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.post("/api/v1/objectives", json={"goal_id": goal, "title": "o"}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.get(f"/api/v1/goals/{goal}", headers=CHAT).json()["status"], "active")

    def test_una_app_solo_consume_aprobaciones_de_su_ambito(self):
        ajena, propia = _uid("a"), _uid("a")
        self.c.post("/api/v1/approvals", json={"authorization_id": ajena, "scope": "gestion_tareas:broker"}, headers=DIRECTOR)
        self.c.post("/api/v1/approvals", json={"authorization_id": propia, "scope": "chatygpt:broker"}, headers=DIRECTOR)
        uso = {"use_id": _uid("u"), "operation_id": _uid("op"), "operation_digest": "d"}
        self.assertEqual(self.c.post("/api/v1/approvals/use", json={**uso, "authorization_id": ajena}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.get(f"/api/v1/approvals/{ajena}/status", headers=DIRECTOR).json()["remaining_uses"], 1)
        self.assertEqual(self.c.post("/api/v1/approvals/use", json={**uso, "authorization_id": propia}, headers=CHAT).status_code, 200)

    def test_una_app_no_relaciona_recursos_ajenos(self):
        gti, mio = _uid("gti"), _uid("chat")
        self.c.put("/api/v1/resources", json={"resource_id": gti, "resource_type": "t", "owner_service": "gestion_tareas"}, headers=DIRECTOR)
        self.c.put("/api/v1/resources", json={"resource_id": mio, "resource_type": "t", "owner_service": "chatygpt"}, headers=CHAT)
        rel = {"relation_type": "usa"}
        self.assertEqual(self.c.post("/api/v1/resources/relations", json={**rel, "source_id": gti, "target_id": mio}, headers=CHAT).status_code, 403)
        self.assertEqual(self.c.post("/api/v1/resources/relations", json={**rel, "source_id": mio, "target_id": gti}, headers=CHAT).status_code, 201)


class TestO3MismaRevision(_ConTokens):

    def test_misma_revision_solo_cambia_enabled(self):
        pid, s = _uid("p"), _uid("s")
        self.c.post("/api/v1/policies", json=_pol(pid, "k", s, "ALLOW"), headers=DIRECTOR)
        self.assertEqual(self.c.post("/api/v1/policies", json=_pol(pid, "k", s, "DENY"), headers=DIRECTOR).status_code, 409)
        self.assertEqual(self.c.post("/api/v1/policies", json=_pol(pid, "k", s, "ALLOW", enabled=False), headers=DIRECTOR).status_code, 200)
        self.assertEqual(self.c.post("/api/v1/policies", json=_pol(pid, "k", s, "DENY", revision=2), headers=DIRECTOR).status_code, 200)


class TestO5FlujoLargo(_ConTokens):

    def test_el_detalle_pide_solo_los_ultimos_y_sabe_el_total(self):
        flow = _uid("largo")
        for i in range(12):
            self.c.post("/api/v1/flows/hops", json={"flow_id": flow, "source_system": "chatygpt", "target_system": "ai_broker",
                                                    "kind": "request", "summary": f"paso {i}"}, headers=CHAT)
        r = self.c.get(f"/api/v1/flows/{flow}", params={"limit": 5}, headers=DIRECTOR).json()
        self.assertEqual((r["total"], [s["summary"] for s in r["steps"]]), (12, [f"paso {i}" for i in range(7, 12)]))
        self.assertEqual(len(self.c.get(f"/api/v1/flows/{flow}", headers=DIRECTOR).json()["steps"]), 12)


class TestO8DirectorEnTokensPorApp(unittest.TestCase):

    def test_director_en_ai_os_api_tokens_es_el_director(self):
        antes = {k: os.environ.get(k) for k in ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS")}
        os.environ.pop("AI_OS_API_TOKEN", None)
        os.environ["AI_OS_API_TOKENS"] = "director=tok-d;chatygpt=tok-c"
        try:
            with TestClient(create_app()) as c:
                r = c.post("/api/v1/policies", json=_pol(_uid("p"), _uid("k"), _uid("s")), headers={"Authorization": "Bearer tok-d"})
                self.assertEqual(r.status_code, 201, r.text)
        finally:
            for k, v in antes.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class TestA05RecursosDeOtraApp(_ConTokens):

    def test_una_app_no_crea_recursos_a_nombre_de_otra(self):
        rid = _uid("gti:task")
        r = self.c.put("/api/v1/resources", json={"resource_id": rid, "resource_type": "task", "owner_service": "gestion_tareas"}, headers=CHAT)
        self.assertEqual(r.status_code, 403, r.text)
        r = self.c.put("/api/v1/resources", json={"resource_id": rid, "resource_type": "task", "owner_service": "gestion_tareas"},
                       headers={"Authorization": "Bearer tok-gti"})
        self.assertEqual(r.status_code, 200, r.text)


class TestA06TokensEnMarcha(unittest.TestCase):

    def test_un_fichero_de_conexion_borrado_no_se_regenera_con_un_token_que_core_rechaza(self):
        carpeta = Path(tempfile.mkdtemp(prefix="conexion_"))
        antes = {k: os.environ.get(k) for k in ("AI_OS_AUTO_TOKENS", "AI_OS_CONNECT_DIR", "AI_OS_API_TOKEN", "AI_OS_API_TOKENS")}
        os.environ.update(AI_OS_AUTO_TOKENS="true", AI_OS_CONNECT_DIR=str(carpeta))
        os.environ.pop("AI_OS_API_TOKEN", None)
        os.environ.pop("AI_OS_API_TOKENS", None)
        try:
            with TestClient(create_app()) as c:
                director = json.loads((carpeta / "director.json").read_text(encoding="utf-8"))["token"]
                (carpeta / "athena.json").unlink()
                self.assertEqual(c.get("/api/v1/flows/apps", headers={"Authorization": f"Bearer {director}"}).status_code, 200)
                self.assertFalse((carpeta / "athena.json").exists(), "se regeneró con un token que este Core no acepta")
        finally:
            for k, v in antes.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v


class TestA11RetencionDelMonitor(unittest.TestCase):

    def test_los_pasos_viejos_se_podan_y_los_recientes_se_quedan(self):
        repo = FlowsRepository(get_db_manager())
        with TestClient(create_app()):
            pass  # migraciones aplicadas
        viejo, nuevo = _uid("viejo"), _uid("nuevo")
        repo.append(flow_id=viejo, kind="request", source="a", target="b")
        repo.append(flow_id=nuevo, kind="request", source="a", target="b")
        hace_100_dias = (datetime.now(timezone.utc) - timedelta(days=100)).isoformat()
        with get_db_manager().transaction() as conn:
            conn.execute("UPDATE flow_events SET at = ? WHERE flow_id = ?;", (hace_100_dias, viejo))
        borrados = repo.prune(days=90)
        self.assertGreaterEqual(borrados, 1)
        self.assertEqual(repo.flow(viejo), [])
        self.assertEqual(len(repo.flow(nuevo)), 1)
        self.assertEqual(repo.prune(days=0), 0, "0 = no podar nunca")


if __name__ == "__main__":
    unittest.main()
