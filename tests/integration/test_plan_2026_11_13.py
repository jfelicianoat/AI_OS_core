"""Plan de cambios del 13-nov-2026: AOS-01 a AOS-05 y AOS-07.
Comentarios en español.
"""

import json
import os
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from fastapi.testclient import TestClient

from ai_os_core import conexion
from ai_os_core.api.dependencies import get_db_manager
from ai_os_core.api.routes import credentials, launcher
from ai_os_core.app import create_app


def _uid(prefijo):
    return f"{prefijo}-{uuid.uuid4().hex[:10]}"


class _Entorno(unittest.TestCase):
    """Guarda y restaura las variables que tocan estas pruebas."""

    VARS = ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS", "AI_OS_AUTO_TOKENS", "AI_OS_CONNECT_DIR", "AI_OS_APPS_FILE")

    def setUp(self):
        self._env = {k: os.environ.get(k) for k in self.VARS}
        os.environ["AI_OS_AUTO_TOKENS"] = "false"
        for k in ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS"):
            os.environ.pop(k, None)
        credentials.reset_for_tests()

    def tearDown(self):
        for k, v in self._env.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        credentials.reset_for_tests()


class TestAos01CabeceraNoAscii(_Entorno):

    def test_authorization_no_ascii_da_401_no_500(self):
        os.environ["AI_OS_API_TOKEN"] = "secreto-de-prueba"
        with TestClient(create_app(), raise_server_exceptions=False) as c:
            r = c.get("/api/v1/goals", headers={"Authorization": "Bearer ñandú".encode("latin-1")})
        self.assertEqual(r.status_code, 401, r.text)
        self.assertEqual(r.json()["error"]["type"], "Unauthorized")


class TestAos02Idempotencia(_Entorno):

    def _app_con_ruta(self, codigos):
        """Core real con una ruta extra que devuelve, por orden, los códigos dados."""
        app = create_app()
        pendientes = list(codigos)

        @app.post("/api/v1/_prueba_idempotencia")
        def _ruta():
            from fastapi.responses import JSONResponse
            codigo = pendientes.pop(0)
            return JSONResponse(status_code=codigo, content={"codigo": codigo})

        return app

    def test_un_403_no_se_repite_tras_aprobarse(self):
        with TestClient(self._app_con_ruta([403, 201]), raise_server_exceptions=False) as c:
            h = {"Idempotency-Key": _uid("k")}
            self.assertEqual(c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers=h).status_code, 403)
            segunda = c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers=h)
        self.assertEqual(segunda.status_code, 201)
        self.assertNotIn("X-Idempotent-Replay", segunda.headers)

    def test_un_201_se_repite(self):
        with TestClient(self._app_con_ruta([201, 201]), raise_server_exceptions=False) as c:
            h = {"Idempotency-Key": _uid("k")}
            c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers=h)
            segunda = c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers=h)
        self.assertEqual(segunda.status_code, 201)
        self.assertEqual(segunda.headers.get("X-Idempotent-Replay"), "true")

    def _fila_vieja(self, c, codigo, edad):
        """Primera llamada para conocer la clave interna; luego se envejece la fila a mano."""
        clave = _uid("k")
        c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers={"Idempotency-Key": clave})
        vieja = (datetime.now(timezone.utc) - edad).isoformat()
        with get_db_manager().transaction() as conn:
            filas = conn.execute("UPDATE idempotency_keys SET response_code = ?, created_at = ? WHERE key LIKE ?;",
                                 (codigo, vieja, f"%{clave}")).rowcount
        self.assertEqual(filas, 1)
        return clave

    def test_una_reserva_huerfana_de_mas_de_10_minutos_no_bloquea(self):
        with TestClient(self._app_con_ruta([201, 201]), raise_server_exceptions=False) as c:
            clave = self._fila_vieja(c, 0, timedelta(minutes=11))
            r = c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers={"Idempotency-Key": clave})
        self.assertEqual(r.status_code, 201, r.text)
        self.assertNotIn("X-Idempotent-Replay", r.headers)

    def test_una_clave_de_hace_25_horas_se_ejecuta_de_nuevo(self):
        with TestClient(self._app_con_ruta([201, 201]), raise_server_exceptions=False) as c:
            clave = self._fila_vieja(c, 201, timedelta(hours=25))
            r = c.post("/api/v1/_prueba_idempotencia", json={"a": 1}, headers={"Idempotency-Key": clave})
        self.assertEqual(r.status_code, 201, r.text)
        self.assertNotIn("X-Idempotent-Replay", r.headers)


class TestAos03TokenDelBroker(_Entorno):

    def setUp(self):
        super().setUp()
        self.app_broker, self.app_sin = _uid("conbroker"), _uid("sinbroker")
        os.environ["AI_OS_API_TOKEN"] = "tok-director-xyz"
        os.environ["AI_OS_API_TOKENS"] = (f"{self.app_broker}=tok-con-broker;{self.app_sin}=tok-sin-broker;"
                                          "agora=tok-agora-123")
        self.c = TestClient(create_app(), raise_server_exceptions=False)
        self.director = {"Authorization": "Bearer tok-director-xyz"}
        self.c.post("/api/v1/policies", headers=self.director, json={
            "policy_id": _uid("p"), "policy_key": _uid("k"), "scope": f"{self.app_broker}:broker",
            "decision_if_matched": "ALLOW", "unconditional": True})
        r = self.c.put("/api/v1/credentials/broker", json={"token": "broker-tok-1"},
                       headers={"Authorization": "Bearer tok-agora-123"})
        self.assertEqual(r.status_code, 200, r.text)

    def _get(self, token):
        return self.c.get("/api/v1/credentials/broker", headers={"Authorization": f"Bearer {token}"}).status_code

    def test_app_con_politica_broker_lo_recibe(self):
        self.assertEqual(self._get("tok-con-broker"), 200)

    def test_app_sin_politica_broker_no_lo_recibe(self):
        self.assertEqual(self._get("tok-sin-broker"), 403)

    def test_director_lo_recibe(self):
        self.assertEqual(self._get("tok-director-xyz"), 200)

    def test_agora_lo_recibe_aunque_no_tenga_politica(self):
        self.assertEqual(self._get("tok-agora-123"), 200)

    def test_sin_auth_solo_desde_este_equipo(self):
        os.environ.pop("AI_OS_API_TOKEN")
        os.environ.pop("AI_OS_API_TOKENS")
        remoto = TestClient(create_app(), raise_server_exceptions=False, client=("192.168.1.99", 5000))
        self.assertEqual(remoto.get("/api/v1/credentials/broker").status_code, 403)
        self.assertEqual(remoto.put("/api/v1/credentials/broker", json={"token": "malicioso-123"}).status_code, 403)


class TestAos04EntornoDeLasApps(_Entorno):

    def setUp(self):
        super().setUp()
        catalogo = {"apps": [
            {"id": "athena", "match": ["athena-x"], "start": ["athena.bat"],
             "env": {"ATHENA_CORE_TOKEN": "{token}"}},
            {"id": "huerfana", "match": ["huerfana-x"], "start": ["h.bat"],
             "env": {"H_CORE_TOKEN": "{token}"}},
        ]}
        carpeta = tempfile.mkdtemp(prefix="aios_apps_")
        ruta = Path(carpeta) / "apps.json"
        ruta.write_text(json.dumps(catalogo), encoding="utf-8")
        os.environ["AI_OS_APPS_FILE"] = str(ruta)
        os.environ["AI_OS_API_TOKEN"] = "abc-director"
        os.environ["AI_OS_API_TOKENS"] = "athena=tok-athena-1"
        self.spawned = []
        for nombre, valor in (("_spawn", lambda cmd, cwd, env: self.spawned.append(env)),
                              ("_command_lines", lambda: [])):
            p = mock.patch.object(launcher, nombre, valor)
            p.start()
            self.addCleanup(p.stop)
        launcher._process_cache["at"] = 0.0
        self.c = TestClient(create_app(), raise_server_exceptions=False)

    def _start(self, app_id):
        r = self.c.post(f"/api/v1/apps/{app_id}/start", headers={"Authorization": "Bearer abc-director"})
        self.assertEqual(r.status_code, 202, r.text)
        return self.spawned[-1]

    def test_la_app_no_hereda_los_tokens_de_core(self):
        env = self._start("athena")
        self.assertNotIn("AI_OS_API_TOKEN", env)
        self.assertNotIn("AI_OS_API_TOKENS", env)
        self.assertEqual(env["ATHENA_CORE_TOKEN"], "tok-athena-1")

    def test_una_app_sin_token_propio_no_recibe_el_del_director(self):
        env = self._start("huerfana")
        self.assertEqual(env["H_CORE_TOKEN"], "")


class TestAos05PararSoloSusProcesos(unittest.TestCase):

    def test_is_app_process(self):
        f = launcher._is_app_process
        self.assertFalse(f("code.exe", "code.exe d:\\x\\model_drift", ["model_drift.gui"]))
        self.assertTrue(f("python.exe", "python -m model_drift.gui", ["model_drift.gui"]))
        self.assertTrue(f("chatygpt.exe", "...", ["chatygpt.exe"]))
        self.assertFalse(f("explorer.exe", "explorer d:\\chatygpt.exe", ["chatygpt.exe"]))


class TestAos07CatalogoEnLaConexion(_Entorno):

    def test_una_app_nueva_del_catalogo_recibe_su_fichero(self):
        carpeta = Path(tempfile.mkdtemp(prefix="aios_cx_"))
        catalogo = carpeta / "apps.json"
        catalogo.write_text(json.dumps({"apps": [{"id": "nueva_app"}, {"id": "remota", "kind": "remote"}]}),
                            encoding="utf-8")
        os.environ["AI_OS_APPS_FILE"] = str(catalogo)
        os.environ["AI_OS_CONNECT_DIR"] = str(carpeta / "conexion")
        conexion.provision({}, 8720)
        self.assertTrue((carpeta / "conexion" / "nueva_app.json").is_file())
        self.assertTrue((carpeta / "conexion" / "athena.json").is_file())  # PRINCIPALS sigue siendo el mínimo
        self.assertFalse((carpeta / "conexion" / "remota.json").exists())


if __name__ == "__main__":
    unittest.main()
