"""Lanzador del monitor (0.3.0): estado de las apps, dependencias y quién puede arrancar.
Comentarios en español.

El arranque real se sustituye por un registro (`_spawn`): las pruebas no abren ventanas.
"""

import json
import os
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

from fastapi.testclient import TestClient
from ai_os_core.app import create_app
from ai_os_core.api.routes import launcher


class _Up(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        self.send_response(401)  # contestar, aunque sea que no, es estar vivo
        self.end_headers()

    def log_message(self, *args):
        pass


class TestLauncher(unittest.TestCase):

    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), _Up)
        threading.Thread(target=self.server.serve_forever, daemon=True).start()
        up = f"http://127.0.0.1:{self.server.server_address[1]}/health"
        catalog = {"apps": [
            {"id": "broker", "name": "Broker", "kind": "remote", "health": up},
            {"id": "agora", "name": "Agora", "health": "http://127.0.0.1:9/health", "start": ["agora.cmd"]},
            {"id": "gti", "name": "GTI", "match": ["gti-que-no-existe.exe"], "start": ["gti.bat"],
             "requires": ["agora"], "uses": ["broker"]},
            {"id": "athena", "name": "Athena", "match": ["athena-que-no-existe"], "start": ["athena.bat"], "cwd": "C:\\",
             "uses": ["agora"], "env": {"ATHENA_CORE_URL": "{core_url}", "ATHENA_CORE_TOKEN": "{token}"}},
            {"id": "base", "name": "Base", "match": ["base-proc"], "start": ["base.bat"]},
            {"id": "cliente", "name": "Cliente", "match": ["cliente-proc"], "start": ["cliente.bat"], "requires": ["base"]},
        ]}
        folder = tempfile.mkdtemp(prefix="aios_apps_")
        self.catalog = os.path.join(folder, "apps.json")
        with open(self.catalog, "w", encoding="utf-8") as fh:
            json.dump(catalog, fh)
        os.environ["AI_OS_APPS_FILE"] = self.catalog
        os.environ["AI_OS_API_TOKEN"] = "tok-director"
        os.environ["AI_OS_API_TOKENS"] = "athena=tok-athena"
        launcher._process_cache["at"] = 0.0
        self.spawned = []
        patcher = mock.patch.object(launcher, "_spawn", lambda cmd, cwd, env: self.spawned.append((cmd, cwd, env)))
        patcher.start()
        self.addCleanup(patcher.stop)
        procesos = mock.patch.object(launcher, "_command_lines", return_value=[])  # sin listar los de verdad
        procesos.start()
        self.addCleanup(procesos.stop)
        self.client = TestClient(create_app(), raise_server_exceptions=False)
        self.client.__enter__()

    def tearDown(self):
        self.client.__exit__(None, None, None)
        self.server.shutdown()
        for key in ("AI_OS_APPS_FILE", "AI_OS_API_TOKEN", "AI_OS_API_TOKENS"):
            del os.environ[key]

    def _apps(self):
        r = self.client.get("/api/v1/apps", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 200, r.text)
        return {a["id"]: a for a in r.json()["apps"]}

    def test_states_and_what_blocks_each_app(self):
        apps = self._apps()
        self.assertTrue(apps["broker"]["running"])        # contesta 401: está viva
        self.assertFalse(apps["broker"]["can_start"])     # remota: se arranca en su equipo
        self.assertFalse(apps["agora"]["running"])
        self.assertTrue(apps["agora"]["can_start"])
        self.assertFalse(apps["gti"]["can_start"])
        self.assertEqual(apps["gti"]["blocked_by"], ["Agora"])
        self.assertEqual(apps["athena"]["warnings"], ["Agora"])  # la usa, pero puede arrancar
        self.assertTrue(apps["athena"]["can_start"])

    def test_requires_blocks_the_start(self):
        r = self.client.post("/api/v1/apps/gti/start", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 409)
        self.assertIn("Agora", r.text)
        self.assertEqual(self.spawned, [])

    def test_start_wires_the_app_to_this_core_with_its_own_token(self):
        r = self.client.post("/api/v1/apps/athena/start", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 202, r.text)
        self.assertEqual(r.json()["warnings"], ["Agora"])
        ((cmd, cwd, env),) = self.spawned
        self.assertEqual((cmd, cwd), (["athena.bat"], "C:\\"))
        self.assertEqual(env["ATHENA_CORE_TOKEN"], "tok-athena")
        self.assertEqual(env["ATHENA_CORE_URL"], "http://testserver")
        # El arranque se ve en el monitor como un paso Core -> Athena
        events = self.client.get("/api/v1/flows/events", headers={"Authorization": "Bearer tok-director"}).json()
        self.assertTrue(any(e["source"] == "core" and e["target"] == "athena" for e in events))

    def test_only_the_director_starts_apps_and_only_from_the_catalog(self):
        r = self.client.post("/api/v1/apps/athena/start", headers={"Authorization": "Bearer tok-athena"})
        self.assertEqual(r.status_code, 403)
        r = self.client.post("/api/v1/apps/athena/start")
        self.assertEqual(r.status_code, 401)
        r = self.client.post("/api/v1/apps/no_existe/start", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 404)
        r = self.client.post("/api/v1/apps/broker/start", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 400)
        self.assertEqual(self.spawned, [])

    def test_a_running_app_is_not_started_twice(self):
        with mock.patch.object(launcher, "_command_lines", return_value=["c:\\x\\athena-que-no-existe --ui"]):
            r = self.client.post("/api/v1/apps/athena/start", headers={"Authorization": "Bearer tok-director"})
        self.assertEqual(r.status_code, 409)
        self.assertEqual(self.spawned, [])

    def _running(self, procs):
        """Simula procesos vivos (PID, línea de comandos) y registra lo que se cerraría."""
        killed = []
        lines = [line for _, line in procs]
        stack = [mock.patch.object(launcher, "_processes", return_value=procs),
                 mock.patch.object(launcher, "_command_lines", return_value=lines),
                 mock.patch.object(launcher, "_kill", lambda pids: killed.extend(pids))]
        for patcher in stack:
            patcher.start()
            self.addCleanup(patcher.stop)
        return killed

    def _stop(self, app_id, token="tok-director", force=False):
        return self.client.post(f"/api/v1/apps/{app_id}/stop" + ("?force=true" if force else ""),
                                headers={"Authorization": f"Bearer {token}"})

    def test_stop_closes_only_the_processes_of_that_app_and_never_core(self):
        killed = self._running([(111, "c:/x/athena-que-no-existe --ui"), (222, "c:/otra/cosa.exe"),
                                (os.getpid(), "python athena-que-no-existe")])
        apps = self._apps()
        self.assertTrue(apps["athena"]["can_stop"])
        self.assertFalse(apps["broker"]["can_stop"])
        r = self._stop("athena")
        self.assertEqual(r.status_code, 202, r.text)
        self.assertEqual(killed, [111])
        events = self.client.get("/api/v1/flows/events", headers={"Authorization": "Bearer tok-director"}).json()
        self.assertTrue(any(e["target"] == "athena" and e["summary"] == "parada" for e in events))

    def test_stopping_something_others_need_asks_first(self):
        killed = self._running([(1, "base-proc"), (2, "cliente-proc")])
        self.assertEqual(self._apps()["base"]["needed_by"], ["Cliente"])
        r = self._stop("base")
        self.assertEqual(r.status_code, 409)
        self.assertIn("Cliente", r.text)
        self.assertEqual(killed, [])
        self.assertEqual(self._stop("base", force=True).status_code, 202)
        self.assertEqual(killed, [1])

    def test_who_can_stop_and_what(self):
        killed = self._running([(1, "base-proc")])
        self.assertEqual(self._stop("base", token="tok-athena").status_code, 403)
        self.assertEqual(self._stop("broker").status_code, 400)
        self.assertEqual(self._stop("no_existe").status_code, 404)
        self.assertEqual(self._stop("cliente").status_code, 409)  # no está en marcha
        self.assertEqual(killed, [])

    def test_no_catalog_means_no_apps(self):
        os.environ["AI_OS_APPS_FILE"] = self.catalog + ".no"
        self.assertEqual(self._apps(), {})


if __name__ == "__main__":
    unittest.main()
