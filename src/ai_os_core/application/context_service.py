"""Servicio de aplicación para Context Engine y ContextPackage reproducible (C12, C21, C22).
Comentarios en español.
"""

import uuid
import hashlib
import json
from typing import List, Dict, Any, Optional
from ai_os_core.domain.context import ContextPackage
from ai_os_core.domain.contracts import ResourceReference, utc_now_iso
from ai_os_core.domain.security import ClassificationLevel, AuthorizationPrincipal
from ai_os_core.infrastructure.db.repositories.context_repo import ContextRepository


class SecurityAccessDeniedError(Exception):
    """Lanzada cuando un principal intenta acceder a un scope o clasificación no autorizada (C21, C22)."""
    pass


class ContextService:
    """Orquesta la construcción, persistencia inmutable y recuperación exacta de paquetes de contexto (C12)."""

    def __init__(self, context_repo: ContextRepository):
        self.context_repo = context_repo

    def build_context_package(
        self,
        goal_id: Optional[str],
        classification_level: ClassificationLevel,
        resources: List[ResourceReference],
        payload: Dict[str, Any],
        principal: AuthorizationPrincipal,
        package_id: Optional[str] = None,
        valid_until: Optional[str] = None
    ) -> ContextPackage:
        """Crea y persiste un ContextPackage inmutable tras validar permisos de seguridad (C12, C21, C22)."""
        # Caso C21: Default DENY para acceso a contexto
        if not principal.can_access_scope("context:build"):
            raise SecurityAccessDeniedError(
                f"Acceso denegado: El principal '{principal.principal_id}' no tiene el scope 'context:build'."
            )

        # Caso C22: Techo de clasificación
        if not principal.can_access_classification(classification_level):
            raise SecurityAccessDeniedError(
                f"Techo de seguridad excedido: clearance '{principal.clearance_level.value}' < solicitado '{classification_level.value}'."
            )

        pid = package_id or f"ctx_{uuid.uuid4().hex[:12]}"
        now = utc_now_iso()

        # Calcular hash determinista del snapshot (C12)
        snapshot_content = {
            "resources": sorted([r.to_dict() for r in resources], key=lambda x: (x["resource_type"], x["resource_id"])),
            "payload": payload,
            "classification": classification_level.value
        }
        serialized = json.dumps(snapshot_content, sort_keys=True)
        snapshot_hash = hashlib.sha256(serialized.encode("utf-8")).hexdigest()

        pkg = ContextPackage(
            package_id=pid,
            goal_id=goal_id,
            classification_level=classification_level,
            snapshot_hash=snapshot_hash,
            resources=resources,
            payload=payload,
            created_at=now,
            valid_until=valid_until
        )

        self.context_repo.save_package(pkg)
        return pkg

    def get_context_package(self, package_id: str) -> Optional[ContextPackage]:
        """Recupera un paquete de contexto por su identificador."""
        return self.context_repo.get_package(package_id)

    def recover_historical_snapshot(self, snapshot_hash: str) -> Optional[ContextPackage]:
        """Recupera la revisión exacta inmutable a partir de su hash histórico (C12)."""
        return self.context_repo.get_by_snapshot_hash(snapshot_hash)
