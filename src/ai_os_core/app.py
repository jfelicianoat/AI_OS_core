"""Punto de entrada principal de la aplicación FastAPI para AI OS Core.
Comentarios en español.
"""

from contextlib import asynccontextmanager
import hashlib
import json
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, Response as FastApiResponse

from .bootstrap import bootstrap_database
from .api.errors import register_exception_handlers, format_error_response
from .api.dependencies import get_idempotency_repo
from .infrastructure.db.repositories.idempotency_repo import IdempotencyConflictError, IdempotencyInProgressError
from .api.routes import health, goals, registry, events, policies, approvals, restore, budget, certifications, context, planner, resources
from . import __version__


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: asegura bootstrap antes de servir peticiones."""
    bootstrap_database()
    yield


def create_app() -> FastAPI:
    """Fábrica de la aplicación FastAPI."""
    app = FastAPI(
        title="AI OS Core Service",
        description="Control Plane determinista, federado y local-first para la plataforma AI OS",
        version=__version__,
        lifespan=lifespan
    )

    # Registro de manejadores de excepciones
    register_exception_handlers(app)

    # Middleware de Idempotencia Atómica (Caso crítico C01)
    @app.middleware("http")
    async def idempotency_middleware(request: Request, call_next):
        idempotency_key = request.headers.get("X-Idempotency-Key") or request.headers.get("Idempotency-Key")

        if not idempotency_key or request.method in ("GET", "HEAD", "OPTIONS"):
            return await call_next(request)

        principal_id = request.headers.get("X-Principal-Id", "anonymous")
        operation_id = request.headers.get("X-Operation-Id", idempotency_key)
        # Namespace normativo (§8): principal + operación + clave. La misma clave usada
        # por otro principal u otra ruta es otra operación, no una repetición.
        namespaced_key = f"{principal_id}|{request.method} {request.url.path}|{idempotency_key}"

        body_bytes = await request.body()
        request_digest = hashlib.sha256(body_bytes).hexdigest()

        idemp_repo = get_idempotency_repo()

        # 1. Reservar la clave o recuperar la respuesta previa. Las excepciones de
        # un middleware no llegan a los exception handlers: se responden aquí.
        try:
            cached = idemp_repo.claim(
                key=namespaced_key,
                principal_id=principal_id,
                operation_id=operation_id,
                request_digest=request_digest
            )
        except IdempotencyConflictError as exc:
            return JSONResponse(status_code=409, content=format_error_response("IdempotencyConflict", str(exc)))
        except IdempotencyInProgressError as exc:
            return JSONResponse(
                status_code=409,
                content=format_error_response("IdempotencyInProgress", str(exc)),
                headers={"Retry-After": "1"}
            )

        if cached:
            cached_code, cached_body = cached
            return FastApiResponse(
                content=cached_body,
                status_code=cached_code,
                media_type="application/json",
                headers={"X-Cache-Hit": "true", "X-Idempotent-Replay": "true"}
            )

        # 2. Procesar solicitud; si revienta, liberar la reserva para permitir el reintento
        try:
            response = await call_next(request)
        except Exception:
            idemp_repo.release(namespaced_key)
            raise

        # 3. Almacenar respuesta si es exitosa o controlada
        if response.status_code < 500:
            res_body = [section async for section in response.body_iterator]
            body_text = b"".join(res_body).decode("utf-8", errors="replace")

            idemp_repo.save_response(
                key=namespaced_key,
                principal_id=principal_id,
                operation_id=operation_id,
                request_digest=request_digest,
                response_code=response.status_code,
                response_body=body_text
            )

            return FastApiResponse(
                content=body_text,
                status_code=response.status_code,
                headers=dict(response.headers),
                media_type=response.media_type
            )

        idemp_repo.release(namespaced_key)
        return response

    # Registro de routers
    app.include_router(health.router)
    app.include_router(goals.router)
    app.include_router(registry.router)
    app.include_router(events.router)
    app.include_router(policies.router)
    app.include_router(approvals.router)
    app.include_router(restore.router)
    app.include_router(budget.router)
    app.include_router(certifications.router)
    app.include_router(context.router)
    app.include_router(planner.router)
    app.include_router(resources.router)

    return app


# Instancia expuesta para servidores ASGI (uvicorn)
app = create_app()
