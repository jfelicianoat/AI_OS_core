"""AOS-06 (plan 13-nov): certificaciones atadas a su evidencia y con caducidad.
Comentarios en español.
"""

import os
import unittest
import uuid
from datetime import datetime, timedelta, timezone

from fastapi.testclient import TestClient

from ai_os_core.api.dependencies import get_db_manager
from ai_os_core.app import create_app

SHA = "a" * 64


class TestCertificacionesEvidencia(unittest.TestCase):

    def setUp(self):
        self._env = {k: os.environ.pop(k, None) for k in ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS")}
        self.c = TestClient(create_app(), raise_server_exceptions=False)

    def tearDown(self):
        for k, v in self._env.items():
            if v is not None:
                os.environ[k] = v

    def _cert(self, **extra):
        return {"model_id": f"m-{uuid.uuid4().hex[:8]}", "capability_id": "c", "version": "1",
                "source_system": "model_drift", "evaluation_verdict": "CERTIFIED", "is_applicable": True, **extra}

    def _url(self, body):
        return f"/api/v1/certifications/{body['model_id']}/c/1"

    def test_guarda_hash_y_caducidad(self):
        futuro = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()
        body = self._cert(evidence_sha256=SHA, expires_at=futuro)
        self.assertEqual(self.c.post("/api/v1/certifications", json=body).status_code, 201)
        leido = self.c.get(self._url(body)).json()
        self.assertEqual(leido["evidence_sha256"], SHA)
        self.assertEqual(leido["evaluation_verdict"], "CERTIFIED")
        self.assertTrue(leido["is_applicable"])

    def test_caducada_se_lee_expired_sin_tocar_lo_guardado(self):
        body = self._cert(expires_at=(datetime.now(timezone.utc) + timedelta(days=1)).isoformat())
        self.assertEqual(self.c.post("/api/v1/certifications", json=body).status_code, 201)
        ayer = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
        with get_db_manager().transaction() as conn:
            conn.execute("UPDATE certification_applicability SET expires_at = ? WHERE model_id = ?;",
                         (ayer, body["model_id"]))
        leido = self.c.get(self._url(body)).json()
        self.assertEqual(leido["evaluation_verdict"], "EXPIRED")
        self.assertFalse(leido["is_applicable"])
        listado = [x for x in self.c.get("/api/v1/certifications").json() if x["model_id"] == body["model_id"]]
        self.assertEqual(listado[0]["evaluation_verdict"], "EXPIRED")
        conn = get_db_manager().get_connection()
        try:
            guardado = conn.execute("SELECT evaluation_verdict FROM certification_applicability WHERE model_id = ?;",
                                    (body["model_id"],)).fetchone()[0]
        finally:
            conn.close()
        self.assertEqual(guardado, "CERTIFIED")

    def test_rechaza_hash_mal_formado_y_caducidad_pasada(self):
        for extra in ({"evidence_sha256": "ABC"}, {"evidence_sha256": "A" * 64},
                      {"expires_at": (datetime.now(timezone.utc) - timedelta(minutes=1)).isoformat()},
                      {"expires_at": "2099-01-01T00:00:00"}):
            with self.subTest(extra=extra):
                self.assertEqual(self.c.post("/api/v1/certifications", json=self._cert(**extra)).status_code, 422)

    def test_sin_campos_nuevos_igual_que_antes(self):
        body = self._cert()
        self.assertEqual(self.c.post("/api/v1/certifications", json=body).status_code, 201)
        leido = self.c.get(self._url(body)).json()
        self.assertIsNone(leido["evidence_sha256"])
        self.assertIsNone(leido["expires_at"])
        self.assertEqual(leido["evaluation_verdict"], "CERTIFIED")


if __name__ == "__main__":
    unittest.main()
