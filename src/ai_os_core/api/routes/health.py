"""Endpoints de estado y salud del servicio.
Comentarios en español.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from ai_os_core.infrastructure.db.connection import DatabaseManager
from ai_os_core.api.dependencies import get_db_manager
from ai_os_core import __version__

router = APIRouter(tags=["Health"])


@router.get("/health")
def get_health():
    """Comprobación de vida (liveness probe)."""
    return {
        "status": "healthy",
        "service": "ai_os_core",
        "version": __version__
    }


@router.get("/ready")
def get_readiness(db: DatabaseManager = Depends(get_db_manager)):
    """Comprobación de preparación (readiness probe): verifica conexión y tablas SQLite."""
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(version) FROM schema_versions;")
        latest_version = cursor.fetchone()[0]
        conn.close()
        return {
            "status": "ready",
            "service": "ai_os_core",
            "schema_version": latest_version or 0
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Base de datos no disponible o sin inicializar: {str(e)}"
        )
