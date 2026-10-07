"""Cliente HTTP seguro con protecciones SSRF y rechazo de reenvío de credenciales (C23).
Comentarios en español.
"""

import ipaddress
from urllib.parse import urlparse
from typing import Optional, List
from ai_os_core.config import settings


class SSRFSecurityViolation(Exception):
    """Lanzada cuando un endpoint infringe la política de seguridad o la allowlist de hosts."""
    pass


class CredentialForwardingError(Exception):
    """Lanzada si se detecta un intento de reenviar credenciales a un host no autorizado."""
    pass


class SecurityHttpClientValidator:
    """Validador estricto de endpoints de servicios registrados (C23)."""

    METADATA_IPS = {
        "169.254.169.254",   # AWS / GCP / Azure metadata
        "fd00:ec2::254",     # AWS IPv6 metadata
    }

    def __init__(self, allowed_hosts: Optional[List[str]] = None, allow_private: Optional[bool] = None):
        self.allowed_hosts = allowed_hosts if allowed_hosts is not None else settings.allowed_service_hosts
        self.allow_private = settings.allow_private_networks if allow_private is None else allow_private

    def validate_url(self, url: str) -> None:
        """Valida que la URL cumpla las políticas SSRF y allowlist.

        Se admiten: hosts de la allowlist, loopback y, si allow_private, redes
        privadas (el ecosistema es local-first: el Broker vive en la LAN). Todo lo
        demás se rechaza, incluidas IPs públicas y nombres DNS fuera de la lista.
        """
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            raise SSRFSecurityViolation(f"Esquema no permitido '{parsed.scheme}'. Solo http y https son válidos.")

        try:
            hostname = parsed.hostname
            parsed.port  # Un puerto ilegible lanza ValueError
        except ValueError:
            raise SSRFSecurityViolation(f"URL mal formada: '{url}'.")
        if not hostname:
            raise SSRFSecurityViolation("URL sin nombre de host válido.")

        try:
            ip = ipaddress.ip_address(hostname)
        except ValueError:
            ip = None

        if ip is None:
            # Nombre DNS: sólo los de la allowlist
            if hostname.lower() not in {h.lower() for h in self.allowed_hosts}:
                raise SSRFSecurityViolation(f"Host '{hostname}' no está en la allowlist de servicios autorizados.")
            return

        # ::ffff:a.b.c.d se evalúa como la IPv4 que encapsula
        if isinstance(ip, ipaddress.IPv6Address) and ip.ipv4_mapped is not None:
            ip = ip.ipv4_mapped

        # 1. Bloqueo de metadatos de nube y rangos que nunca son un servicio legítimo
        if str(ip) in self.METADATA_IPS or ip.is_link_local:
            raise SSRFSecurityViolation(f"Acceso bloqueado a dirección link-local/metadatos de nube: {hostname}")
        if ip.is_unspecified or ip.is_multicast or ip.is_reserved:
            raise SSRFSecurityViolation(f"Dirección no enrutable como servicio: {hostname}")

        # 2. Allowlist explícita, loopback y redes privadas
        if str(ip) in self.allowed_hosts or ip.is_loopback:
            return
        if ip.is_private:
            if not self.allow_private:
                raise SSRFSecurityViolation(f"Acceso denegado a red privada: {hostname}")
            return
        raise SSRFSecurityViolation(f"IP pública '{hostname}' fuera de la allowlist de servicios autorizados.")

    def sanitize_headers_for_redirect(self, headers: dict[str, str], original_url: str, target_url: str) -> dict[str, str]:
        """Elimina cabeceras de autorización y credenciales al redirigir entre hosts distintos (C23)."""
        orig_host = urlparse(original_url).hostname
        target_host = urlparse(target_url).hostname

        if orig_host != target_host:
            sanitized = {k: v for k, v in headers.items() if k.lower() not in ("authorization", "cookie", "x-api-key")}
            return sanitized
        return headers
