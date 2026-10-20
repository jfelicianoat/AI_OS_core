"""Paquete de pruebas de AI OS Core.

Antes de que nada importe ai_os_core se redirige la BD a un fichero temporal: la
configuración se lee al importar, y sin esto el smoke test escribía metas de
prueba en la base real (%LOCALAPPDATA%/AIOSCore/data/ai_os_core.db).
"""

import os
import tempfile

if "AI_OS_DB_PATH" not in os.environ:
    os.environ["AI_OS_DB_PATH"] = os.path.join(
        tempfile.mkdtemp(prefix="ai_os_core_tests_"), "ai_os_core_test.db"
    )

# Core genera tokens por app en %LOCALAPPDATA%\AIOSCore\conexion: los tests no tocan el perfil real
# (y con tokens generados toda la API pediría credencial). Quien lo prueba lo activa con su carpeta.
os.environ.setdefault("AI_OS_AUTO_TOKENS", "false")
# Los tokens reales del usuario (variables de entorno) cerrarían la API a los tests que no los mandan
for _var in ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS"):
    os.environ.pop(_var, None)
