"""Arranque con el puerto ocupado: Core debe decir quién lo tiene, no morir con un error de uvicorn.

El 5-nov-2026 ComfyUI Desktop ocupaba el 8000 y Core no arrancaba sin explicar por qué.
"""
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
