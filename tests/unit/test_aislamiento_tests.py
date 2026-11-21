"""A-00 (auditoría 19-nov): lanzar los tests con unittest desde cualquier carpeta raíz no toca el perfil real.

`python -m unittest discover -s tests` no importa `tests/__init__.py`; sin otra protección los
tests escribían en la base real y en la carpeta de conexión con los tokens del usuario.
"""

import runpy, pathlib; runpy.run_path(str(pathlib.Path(__file__).resolve().parents[1] / "__init__.py"))  # aislamiento (ver tests/__init__.py), se lance como se lance
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


class AislamientoTests(unittest.TestCase):
    def test_unittest_discover_from_any_folder_never_touches_the_profile(self):
        # Arbitraje O-1: desde tests/integration el __init__.py del subpaquete tampoco se importa
        for carpeta, patron in (("tests", "test_api_smoke.py"), ("tests/integration", "test_api_smoke.py"),
                                ("tests/unit", "test_contracts.py")):
            with self.subTest(carpeta=carpeta):
                perfil = Path(tempfile.mkdtemp(prefix="perfil_falso_"))
                env = {k: v for k, v in os.environ.items() if not k.startswith("AI_OS_")}
                # Un usuario con sus tokens, tokens automáticos y su propia base en el perfil
                env.update(LOCALAPPDATA=str(perfil), PYTHONPATH=str(REPO / "src"), AI_OS_AUTO_TOKENS="true",
                           AI_OS_DB_PATH=str(perfil / "AIOSCore" / "data" / "real.db"),
                           AI_OS_API_TOKEN="token-real-del-usuario", AI_OS_API_TOKENS="athena=otro-real")
                r = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", carpeta, "-p", patron],
                                   cwd=REPO, env=env, capture_output=True, text=True, timeout=300)
                tocados = [str(p.relative_to(perfil)) for p in perfil.rglob("*")]
                self.assertEqual(tocados, [], f"los tests escribieron en el perfil: {tocados}\n{r.stderr[-800:]}")
                self.assertEqual(r.returncode, 0, r.stderr[-1500:])


if __name__ == "__main__":
    unittest.main()
