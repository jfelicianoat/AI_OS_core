"""Servicio de aplicación para el Grafo de Recursos e Identidad Federada (M0-GRAPH, C24).
Comentarios en español.
"""

from typing import Optional, List
from ..domain.resources import ResourceNode, ResourceRelation
from ..domain.contracts import IdentityBinding
from ..infrastructure.db.repositories.resources_repo import ResourcesRepository


class ResourceService:
    """Orquesta operaciones sobre el Resource Graph ligero y bindings de identidad nativa."""

    def __init__(self, resources_repo: ResourcesRepository):
        self.resources_repo = resources_repo

    def save_resource(self, resource: ResourceNode) -> ResourceNode:
        """Guarda un recurso federado preservando la autoridad del propietario."""
        self.resources_repo.save_resource(resource)
        return resource

    def get_resource(self, resource_id: str) -> Optional[ResourceNode]:
        """Obtiene un recurso por su identificador."""
        return self.resources_repo.get_resource(resource_id)

    def add_relation(self, relation: ResourceRelation) -> ResourceRelation:
        """Añade una relación entre recursos."""
        self.resources_repo.add_relation(relation)
        return relation

    def get_relations_for(self, source_id: str) -> List[ResourceRelation]:
        """Consulta relaciones del recurso."""
        return self.resources_repo.get_relations_for(source_id)

    def bind_identity(self, binding: IdentityBinding) -> IdentityBinding:
        """Registra la vinculación de identidad nativa asegurando la revisión de adaptador (C24)."""
        self.resources_repo.save_identity_binding(binding)
        return binding

    def get_identity_binding(self, global_id: str, source_system: str) -> Optional[IdentityBinding]:
        """Recupera la vinculación de identidad."""
        return self.resources_repo.get_identity_binding(global_id, source_system)
