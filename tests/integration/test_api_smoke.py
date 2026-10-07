"""Prueba de humo (smoke test) para la API FastAPI de AI OS Core.
Comentarios en español.
"""

import unittest
from fastapi.testclient import TestClient
from ai_os_core.app import create_app


class TestApiSmoke(unittest.TestCase):
    """Verifica que la aplicación FastAPI arranca y responde correctamente a las peticiones HTTP."""

    def setUp(self):
        self.app = create_app()
        self.client = TestClient(self.app)

    def test_health_endpoint(self):
        """Verifica que /health responde con estado 200 y status healthy."""
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["service"], "ai_os_core")

    def test_ready_endpoint(self):
        """Verifica que /ready confirma que la base de datos está migrada."""
        with TestClient(self.app) as client:
            response = client.get("/ready")
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertEqual(data["status"], "ready")
            self.assertGreaterEqual(data["schema_version"], 1)

    def test_goals_api_crud(self):
        """Verifica el flujo CRUD básico para Goals a través de la API HTTP."""
        with TestClient(self.app) as client:
            # Crear Goal
            payload = {
                "title": "Meta Smoke Test",
                "description": "Validación de endpoints REST",
                "owner_service": "test_suite"
            }
            res_post = client.post("/api/v1/goals", json=payload)
            self.assertEqual(res_post.status_code, 201)
            created = res_post.json()
            goal_id = created["id"]
            self.assertEqual(created["title"], "Meta Smoke Test")

            # Obtener Goal
            res_get = client.get(f"/api/v1/goals/{goal_id}")
            self.assertEqual(res_get.status_code, 200)
            self.assertEqual(res_get.json()["id"], goal_id)

            # Listar Goals
            res_list = client.get("/api/v1/goals")
            self.assertEqual(res_list.status_code, 200)
            items = res_list.json()["items"]
            self.assertTrue(any(g["id"] == goal_id for g in items))


if __name__ == "__main__":
    unittest.main()
