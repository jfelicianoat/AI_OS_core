"""Proveedor de reloj determinista para pruebas y producción.
Comentarios en español.
"""

from datetime import datetime, timezone
from typing import Optional


class Clock:
    """Reloj configurable para garantizar pruebas reproducibles."""
    def __init__(self, fixed_time: Optional[datetime] = None):
        self._fixed_time = fixed_time

    def now(self) -> datetime:
        """Devuelve la fecha actual o el tiempo fijado para pruebas."""
        if self._fixed_time:
            return self._fixed_time
        return datetime.now(timezone.utc)

    def now_iso(self) -> str:
        """Devuelve la fecha actual en formato ISO 8601 UTC."""
        return self.now().isoformat()

    def set_time(self, new_time: Optional[datetime]) -> None:
        """Permite avanzar o fijar el tiempo durante tests."""
        self._fixed_time = new_time


# Instancia por defecto
system_clock = Clock()
