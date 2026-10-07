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
