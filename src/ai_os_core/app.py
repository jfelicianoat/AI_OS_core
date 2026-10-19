"""Punto de entrada principal de la aplicación FastAPI para AI OS Core.
Comentarios en español.
"""

from contextlib import asynccontextmanager
import hashlib
import hmac
import json
import os
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse, Response as FastApiResponse

from .bootstrap import bootstrap_database
from .api.errors import register_exception_handlers, format_error_response
from .api.dependencies import get_idempotency_repo, TokenGrant
from .domain.security import ClassificationLevel
from .infrastructure.db.repositories.idempotency_repo import IdempotencyConflictError, IdempotencyInProgressError
from .api.routes import health, goals, registry, events, policies, approvals, restore, budget, certifications, context, planner, resources, flows, launcher
from . import __version__


# Rutas sin token: sondas de vida y documentación (no exponen datos).
_PUBLIC_PATHS = {"/health", "/ready", "/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect", "/monitor"}
# La página del monitor y sus iconos no llevan datos: los datos se piden con token desde ella.
_PUBLIC_PREFIXES = ("/monitor/",)


def _load_tokens() -> dict:
    """Tokens admitidos -> TokenGrant (principal None para el token común sin identidad).

    AI_OS_API_TOKEN: un token compartido. AI_OS_API_TOKENS: "app=token;otra_app=token2",
    un token por app, que fija quién llama. Opcionalmente "app=token|scope1,scope2|CLEARANCE"
    limita qué scopes y qué nivel de clasificación puede pedir esa app.
    """
    tokens = {}
    shared = os.getenv("AI_OS_API_TOKEN", "").strip()
    if shared:
        tokens[shared] = TokenGrant(principal=None)
    for item in os.getenv("AI_OS_API_TOKENS", "").split(";"):
        principal, sep, rest = item.partition("=")
        token, _, limits = rest.partition("|")
        scopes, _, clearance = limits.partition("|")
        if sep and principal.strip() and token.strip():
            clearance = clearance.strip() or None
            if clearance is not None:
                ClassificationLevel(clearance)  # un nivel mal escrito impide arrancar: no se abre de más
            tokens[token.strip()] = TokenGrant(
                principal=principal.strip(),
                scopes=frozenset(s.strip() for s in scopes.split(",") if s.strip()) if scopes.strip() else None,
                clearance=clearance
            )
    return tokens


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

    # Autenticación opcional por token (registrada después: Starlette la ejecuta antes que la
    # idempotencia, así una petición sin credencial no reserva claves). Sin AI_OS_API_TOKEN ni
    # AI_OS_API_TOKENS la API queda abierta como en 0.2.0, pensada sólo para 127.0.0.1.
    tokens = _load_tokens()
    if tokens:
        @app.middleware("http")
        async def token_middleware(request: Request, call_next):
            if request.url.path in _PUBLIC_PATHS or request.url.path.startswith(_PUBLIC_PREFIXES):
                return await call_next(request)
            scheme, _, supplied = request.headers.get("Authorization", "").partition(" ")
            supplied = supplied.strip()
            matched, grant = False, None
            for token, owner in tokens.items():  # sin salida temprana: todas las comparaciones cuestan igual
                if hmac.compare_digest(supplied, token):
                    matched, grant = True, owner
            principal = grant.principal if grant else None
            request.state.token_grant = grant  # lo leen las rutas que reciben scopes o clearance
            if scheme.lower() != "bearer" or not matched:
                return JSONResponse(
                    status_code=401,
                    content=format_error_response("Unauthorized", "Falta el token de AI OS Core o no es válido."),
                    headers={"WWW-Authenticate": "Bearer"}
                )
            if principal:
                # Token con identidad: la app no puede declararse otra en la cabecera ni en el cuerpo
                declared = request.headers.get("X-Principal-Id")
                claims = [declared]
                if request.method in ("POST", "PUT", "PATCH"):
                    try:
                        body = json.loads(await request.body() or b"null")
                        if isinstance(body, dict):
                            # Quien certifica (source_system) o produce eventos (producer_id) es la app del token
                            claims += [body.get(k) for k in ("principal_id", "source_system", "producer_id")]
                    except ValueError:
                        pass  # el cuerpo ilegible lo rechaza la validación de la ruta
                for claimed in claims:
                    if claimed is not None and claimed != principal:
                        return JSONResponse(
                            status_code=403,
                            content=format_error_response(
                                "PrincipalMismatch", f"El token pertenece a '{principal}', no a '{claimed}'."
                            )
                        )
                if declared is None:
                    # La idempotencia separa claves por principal: que use el del token
                    request.scope["headers"].append((b"x-principal-id", principal.encode()))
            return await call_next(request)

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
    app.include_router(flows.router)
    app.include_router(flows.page_router)
    app.include_router(launcher.router)

    return app


# Instancia expuesta para servidores ASGI (uvicorn)
app = create_app()
