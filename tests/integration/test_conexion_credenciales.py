"""0.4.0: ninguna app necesita que le peguen un token.

Core genera un token por app y lo deja con su URL en la carpeta de conexión; el runner de
Agora publica el token del AI Broker y las apps lo piden. Comentarios en español.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path

from fastapi.testclient import TestClient
from ai_os_core import conexion
from ai_os_core.app import create_app
from ai_os_core.api.routes import credentials


class TestConexionAutomatica(unittest.TestCase):

    def setUp(self):
        self.folder = Path(tempfile.mkdtemp(prefix="aios_conexion_"))
        self._env = {k: os.environ.get(k) for k in ("AI_OS_AUTO_TOKENS", "AI_OS_CONNECT_DIR", "AI_OS_API_TOKENS", "AI_OS_API_TOKEN")}
        os.environ.update(AI_OS_AUTO_TOKENS="true", AI_OS_CONNECT_DIR=str(self.folder))
        os.environ.pop("AI_OS_API_TOKENS", None)
        os.environ.pop("AI_OS_API_TOKEN", None)
        credentials.reset_for_tests()

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        credentials.reset_for_tests()

    def _token(self, principal):
        return json.loads((self.folder / f"{principal}.json").read_text(encoding="utf-8"))["token"]

    def _auth(self, principal):
        return {"Authorization": f"Bearer {self._token(principal)}"}

    def test_cada_app_recibe_su_token_y_se_conserva(self):
        with TestClient(create_app(), raise_server_exceptions=False) as c:
            for p in ("director", *conexion.PRINCIPALS):
                data = json.loads((self.folder / f"{p}.json").read_text(encoding="utf-8"))
                self.assertEqual(data["core_url"], "http://127.0.0.1:8000")
                self.assertGreaterEqual(len(data["token"]), 32)
            # Con tokens generados la API exige credencial, y el token fija quién llama
            self.assertEqual(c.get("/api/v1/goals").status_code, 401)
            self.assertEqual(c.get("/api/v1/goals", headers=self._auth("athena")).status_code, 200)
            r = c.get("/api/v1/goals", headers={**self._auth("athena"), "X-Principal-Id": "chatygpt"})
            self.assertEqual(r.status_code, 403)
        antes = self._token("athena")
        create_app()  # otro arranque: el token no cambia (las apps abiertas siguen valiendo)
        self.assertEqual(self._token("athena"), antes)

    def test_token_fijado_a_mano_manda_y_se_publica(self):
        os.environ["AI_OS_API_TOKENS"] = "gestion_tareas=tok-gti-fijo-123"
        create_app()
        self.assertEqual(self._token("gestion_tareas"), "tok-gti-fijo-123")

    def test_token_del_broker_lo_publica_el_runner_y_lo_leen_las_apps(self):
        with TestClient(create_app(), raise_server_exceptions=False) as c:
            url = "/api/v1/credentials/broker"
            self.assertEqual(c.get(url, headers=self._auth("chatygpt")).status_code, 503)
            # Una app no puede envenenar el token que usan las demás
            r = c.put(url, json={"token": "falso-12345678"}, headers=self._auth("chatygpt"))
            self.assertEqual(r.status_code, 403)
            self.assertEqual(c.put(url, json={"token": "x"}, headers=self._auth("agora")).status_code, 422)
            r = c.put(url, json={"token": "broker-tok-1"}, headers=self._auth("agora"))
            self.assertEqual(r.status_code, 200, r.text)
            self.assertTrue(r.json()["changed"])
            self.assertFalse(c.put(url, json={"token": "broker-tok-1"}, headers=self._auth("agora")).json()["changed"])
            got = c.get(url, headers=self._auth("chatygpt"))
            self.assertEqual(got.json()["token"], "broker-tok-1")
            self.assertEqual(got.json()["published_by"], "agora")
            c.put(url, json={"token": "broker-tok-2"}, headers=self._auth("agora"))  # el Broker se reinició
            self.assertEqual(c.get(url, headers=self._auth("model_drift")).json()["token"], "broker-tok-2")
            self.assertEqual(c.get(url).status_code, 401)


if __name__ == "__main__":
    unittest.main()
