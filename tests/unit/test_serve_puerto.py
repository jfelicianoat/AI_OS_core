"""Arranque con el puerto ocupado: Core debe decir quién lo tiene, no morir con un error de uvicorn.

El 5-nov-2026 ComfyUI Desktop ocupaba el 8000 y Core no arrancaba sin explicar por qué.
"""
import runpy, pathlib; runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] / "__init__.py"))  # aislamiento (ver tests/__init__.py), se lance como se lance
import os
import socket
import unittest

from ai_os_core import serve


class PuertoOcupado(unittest.TestCase):
    def test_dice_quien_ocupa_el_puerto(self):
        ocupante = socket.socket()
        ocupante.bind(("127.0.0.1", 0))
        ocupante.listen()
        puerto = ocupante.getsockname()[1]
        try:
            motivo = serve.puerto_ocupado(puerto)
        finally:
            ocupante.close()
        self.assertIsNotNone(motivo)
        self.assertIn(str(puerto), motivo)
        self.assertIn(str(os.getpid()), motivo)  # el proceso que lo tiene (este, en el test)
        self.assertIn("AI_OS_PORT", motivo)

    def test_puerto_libre(self):
        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        puerto = s.getsockname()[1]
        s.close()
        self.assertIsNone(serve.puerto_ocupado(puerto))


if __name__ == "__main__":
    unittest.main()


class AbrirDocumentacion(unittest.TestCase):
    """A-16 (auditoría 19-nov): `run.bat docs` abría Swagger antes de que Core contestara."""

    def test_abre_docs_solo_cuando_core_contesta(self):
        from unittest import mock
        orden = []
        intentos = iter([OSError("aún no"), OSError("aún no"), mock.MagicMock()])

        def urlopen(url, timeout):
            orden.append(("health", url))
            r = next(intentos)
            if isinstance(r, Exception):
                raise r
            return r

        with mock.patch.object(serve.urllib.request, "urlopen", urlopen), \
                mock.patch.object(serve.time, "sleep", lambda s: None), \
                mock.patch.object(serve.webbrowser, "open", lambda url: orden.append(("abre", url))):
            serve._open_monitor(8720, "docs")
        self.assertEqual(orden[-1], ("abre", "http://127.0.0.1:8720/docs"))
        self.assertEqual([k for k, _ in orden].count("health"), 3)
