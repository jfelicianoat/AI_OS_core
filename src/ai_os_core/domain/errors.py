"""Errores de dominio comunes con traducción HTTP estable.
Comentarios en español.
"""


class ConflictError(Exception):
    """La operación choca con el estado ya registrado (HTTP 409): duplicado, revisión obsoleta, etc."""
    pass


class NotFoundError(Exception):
    """El recurso referido no existe (HTTP 404)."""
    pass
