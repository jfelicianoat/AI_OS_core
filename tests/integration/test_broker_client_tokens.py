"""0.5.0: cada app recibe su token de cliente del AI Broker, no el de administración.

El Broker se simula sustituyendo `broker_client_tokens._call`: nunca se habla con el real.
Comentarios en español.
"""

import runpy, pathlib; runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] / "__init__.py"))  # aislamiento
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient
from ai_os_core import broker_client_tokens as bct
from ai_os_core.app import create_app
from ai_os_core.api.routes import credentials

BASE = "https://broker.prueba:8765"
ADMIN = "admin-tok-1"


class BrokerFalso:
    """Lo justo de §3.2: emitir, listar, revocar y auth/check."""

    def __init__(self):
        self.tokens = {}  # id -> {name, token, active}
        self.reachable = True
        self.calls = []

    def __call__(self, method, url, token, body=None):
        if not self.reachable:
            raise bct.BrokerUnreachable("sin red")
        path = url[len(BASE):]
        self.calls.append((method, path))
        if path == "/api/v1/auth/check":
            for item in self.tokens.values():
                if item["token"] == token and item["active"]:
                    return 200, {"authenticated": True, "auth_required": True, "scope": "client", "client_name": item["name"]}
            if token == ADMIN:
                return 200, {"authenticated": True, "auth_required": True, "scope": "admin", "client_name": None}
            return 403, {"code": "ADMIN_AUTH_REQUIRED"}
        if token != ADMIN:
            return 403, {"code": "ADMIN_AUTH_REQUIRED"}
        if path == "/api/v1/admin/client-tokens" and method == "POST":
            if any(i["name"] == body["name"] and i["active"] for i in self.tokens.values()):
                return 409, {"code": "CLIENT_TOKEN_NAME_TAKEN"}
            new_id = str(len(self.tokens) + 1)
            self.tokens[new_id] = {"name": body["name"], "token": f"abk_{body['name']}_{new_id}", "active": True}
            return 201, {"id": new_id, "name": body["name"], "token": self.tokens[new_id]["token"]}
        if path == "/api/v1/admin/client-tokens" and method == "GET":
            return 200, [{"id": i, "name": t["name"], "active": t["active"]} for i, t in self.tokens.items()]
        if path.startswith("/api/v1/admin/client-tokens/") and method == "DELETE":
            self.tokens[path.rsplit("/", 1)[1]]["active"] = False
            return 200, {}
        return 404, {}


class TestTokensDeCliente(unittest.TestCase):

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="aios_bct_"))
        self._env = {k: os.environ.get(k) for k in ("AI_OS_AUTO_TOKENS", "AI_OS_CONNECT_DIR", "AI_OS_BROKER_URL")}
        os.environ.update(AI_OS_AUTO_TOKENS="true", AI_OS_CONNECT_DIR=str(self.folder), AI_OS_BROKER_URL=BASE)
        self.store = Path(tempfile.mkdtemp(prefix="aios_bct_store_")) / "broker_client_tokens.json"
        self.broker = BrokerFalso()
        self._patches = [mock.patch.object(bct, "_call", self.broker), mock.patch.object(bct, "_store_path", lambda: self.store)]
        for p in self._patches:
            p.start()
        credentials.reset_for_tests()

    def tearDown(self):
        for p in self._patches:
            p.stop()
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        credentials.reset_for_tests()

    def _auth(self, principal):
        token = json.loads((self.folder / f"{principal}.json").read_text(encoding="utf-8"))["token"]
        return {"Authorization": f"Bearer {token}"}

    def _client(self):
        c = TestClient(create_app(), raise_server_exceptions=False)
        for app in ("chatygpt", "model_drift"):
            c.post("/api/v1/policies", headers=self._auth("director"), json={
                "policy_id": f"eco_{app}_base", "policy_key": f"{app}_base", "scope": f"{app}:broker",
                "decision_if_matched": "ALLOW", "unconditional": True})
        return c

    def test_cada_app_recibe_su_token_de_cliente_y_se_reutiliza(self):
        url = "/api/v1/credentials/broker"
        with self._client() as c:
            c.put(url, json={"token": ADMIN}, headers=self._auth("agora"))
            got = c.get(url, headers=self._auth("chatygpt")).json()
            self.assertEqual(got["scope"], "client")
            self.assertEqual(got["client_name"], "chatygpt")
            self.assertTrue(got["token"].startswith("abk_chatygpt"))
            otra = c.get(url, headers=self._auth("model_drift")).json()
            self.assertNotEqual(otra["token"], got["token"])
            # El runner y el director siguen con el de administración
            self.assertEqual(c.get(url, headers=self._auth("agora")).json()["token"], ADMIN)
            self.assertEqual(c.get(url, headers=self._auth("director")).json()["scope"], "admin")
            # Segunda petición: se comprueba y se reutiliza, no se emite otro
            emitidos = len(self.broker.tokens)
            self.assertEqual(c.get(url, headers=self._auth("chatygpt")).json()["token"], got["token"])
            self.assertEqual(len(self.broker.tokens), emitidos)
        # Core se reinicia y el runner aún no ha publicado: el token de cliente sigue saliendo
        credentials.reset_for_tests()
        with self._client() as c:
            again = c.get(url, headers=self._auth("chatygpt"))
            self.assertEqual(again.status_code, 200, again.text)
            self.assertEqual(again.json()["token"], got["token"])

    def test_revocado_por_el_operador_se_emite_otro(self):
        url = "/api/v1/credentials/broker"
        with self._client() as c:
            c.put(url, json={"token": ADMIN}, headers=self._auth("agora"))
            primero = c.get(url, headers=self._auth("chatygpt")).json()["token"]
            for item in self.broker.tokens.values():
                item["active"] = False  # DELETE /admin/client-tokens/{id} desde el panel
            segundo = c.get(url, headers=self._auth("chatygpt")).json()
            self.assertEqual(segundo["scope"], "client")
            self.assertNotEqual(segundo["token"], primero)

    def test_nombre_ocupado_sin_valor_guardado_se_revoca_y_se_reemite(self):
        url = "/api/v1/credentials/broker"
        with self._client() as c:
            c.put(url, json={"token": ADMIN}, headers=self._auth("agora"))
            c.get(url, headers=self._auth("chatygpt"))
            self.store.unlink()  # Core perdió el fichero: el Broker tiene uno activo con ese nombre
            got = c.get(url, headers=self._auth("chatygpt")).json()
            self.assertEqual(got["scope"], "client")
            activos = [t for t in self.broker.tokens.values() if t["name"] == "chatygpt" and t["active"]]
            self.assertEqual([t["token"] for t in activos], [got["token"]])
            self.assertIn(("DELETE", "/api/v1/admin/client-tokens/1"), self.broker.calls)

    def test_sin_broker_alcanzable_sigue_el_token_de_administracion(self):
        url = "/api/v1/credentials/broker"
        self.broker.reachable = False
        with self._client() as c:
            c.put(url, json={"token": ADMIN}, headers=self._auth("agora"))
            got = c.get(url, headers=self._auth("chatygpt")).json()
            self.assertEqual((got["token"], got["scope"]), (ADMIN, "admin"))

    def test_desactivado_no_llama_al_broker(self):
        os.environ["AI_OS_BROKER_URL"] = "off"
        url = "/api/v1/credentials/broker"
        with self._client() as c:
            c.put(url, json={"token": ADMIN}, headers=self._auth("agora"))
            self.assertEqual(c.get(url, headers=self._auth("chatygpt")).json()["scope"], "admin")
        self.assertEqual(self.broker.calls, [])

    def test_url_del_catalogo(self):
        os.environ.pop("AI_OS_BROKER_URL")
        self.assertEqual(bct.broker_url(), "https://192.168.1.52:8765")


if __name__ == "__main__":
    unittest.main()
