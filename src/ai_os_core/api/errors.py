"""Manejo centralizado de excepciones y mapeo de códigos HTTP.
Comentarios en español.
"""

from typing import Any, Dict
try:
    from fastapi import Request, status
    from fastapi.responses import JSONResponse
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False


def format_error_response(error_type: str, message: str, details: Dict[str, Any] | None = None) -> Dict[str, Any]:
    """Genera una estructura de error estandarizada para toda la API."""
    return {
        "error": {
            "type": error_type,
            "message": message,
            "details": details or {}
        }
    }


def register_exception_handlers(app: Any) -> None:
    """Registra manejadores de excepciones en la aplicación FastAPI."""
    if not HAS_FASTAPI:
        return

    from ..infrastructure.db.repositories.idempotency_repo import IdempotencyConflictError
    from ..infrastructure.db.repositories.approvals_repo import ApprovalConflictError, ApprovalExecutionDeniedError
    from ..infrastructure.http.security_client import SSRFSecurityViolation
    from ..domain.errors import ConflictError, NotFoundError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    import sqlite3

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        # Mismo sobre de error que el resto de la API; se conserva "detail" porque
        # es lo que FastAPI devolvía antes y algún cliente puede leerlo.
        content = format_error_response("HTTPError", str(exc.detail))
        content["detail"] = exc.detail
        return JSONResponse(status_code=exc.status_code, content=content, headers=getattr(exc, "headers", None))

    @app.exception_handler(IdempotencyConflictError)
    async def idempotency_conflict_handler(request: Request, exc: IdempotencyConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_error_response("IdempotencyConflict", str(exc))
        )

    @app.exception_handler(ApprovalConflictError)
    async def approval_conflict_handler(request: Request, exc: ApprovalConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_error_response("ApprovalConflict", str(exc))
        )

    @app.exception_handler(ApprovalExecutionDeniedError)
    async def approval_denied_handler(request: Request, exc: ApprovalExecutionDeniedError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=format_error_response("ApprovalDenied", str(exc))
        )

    @app.exception_handler(SSRFSecurityViolation)
    async def ssrf_violation_handler(request: Request, exc: SSRFSecurityViolation):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_error_response("SSRFSecurityViolation", str(exc))
        )

    @app.exception_handler(ConflictError)
    async def conflict_handler(request: Request, exc: ConflictError):
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_error_response("Conflict", str(exc))
        )

    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=format_error_response("NotFound", str(exc))
        )

    @app.exception_handler(sqlite3.IntegrityError)
    async def integrity_handler(request: Request, exc: sqlite3.IntegrityError):
        # Red de seguridad: una restricción de la BD violada es un conflicto del
        # cliente (identificador repetido, referencia inexistente), no un 500.
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=format_error_response("IntegrityConflict", str(exc))
        )

    @app.exception_handler(ValueError)
    async def value_error_handler(request: Request, exc: ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=format_error_response("ValidationError", str(exc))
        )
