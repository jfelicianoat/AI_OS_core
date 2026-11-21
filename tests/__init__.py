"""Paquete de pruebas de AI OS Core.

Antes de que nada importe ai_os_core se redirige la BD a un fichero temporal: la
configuración se lee al importar, y sin esto el smoke test escribía metas de
prueba en la base real (%LOCALAPPDATA%/AIOSCore/data/ai_os_core.db).
"""

import os
import tempfile

# Se ejecuta una vez por proceso, también si unittest descubre desde tests/unit o tests/integration
# (cada módulo de test lo carga en su primera línea): nunca la base ni la carpeta de conexión reales,
# aunque el usuario tenga AI_OS_DB_PATH, AI_OS_CONNECT_DIR o AI_OS_AUTO_TOKENS en su entorno.
if os.environ.get("AI_OS_TESTS_AISLADOS") != "1":
    _tmp = tempfile.mkdtemp(prefix="ai_os_core_tests_")
    os.environ["AI_OS_DB_PATH"] = os.path.join(_tmp, "ai_os_core_test.db")
    os.environ["AI_OS_CONNECT_DIR"] = os.path.join(_tmp, "conexion")
    # Con tokens generados toda la API pediría credencial; quien lo prueba lo activa con su carpeta
    os.environ["AI_OS_AUTO_TOKENS"] = "false"
    os.environ["AI_OS_TESTS_AISLADOS"] = "1"
# Los tokens reales del usuario (variables de entorno) cerrarían la API a los tests que no los mandan
for _var in ("AI_OS_API_TOKEN", "AI_OS_API_TOKENS"):
    os.environ.pop(_var, None)
# Nunca emitir tokens de cliente contra el Broker real del catálogo; quien lo prueba fija una URL falsa
os.environ["AI_OS_BROKER_URL"] = "off"
