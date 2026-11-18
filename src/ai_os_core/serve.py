"""Arranque de Core: HTTP sólo para este equipo y, si se abre a la red, HTTPS para la red.

Las apps de este equipo hablan con http://127.0.0.1:<AI_OS_PORT>. Con AI_OS_HOST distinto de
127.0.0.1 (el runner de Agora del PC IA tiene que llegar) se abre además HTTPS en
AI_OS_HOST:<AI_OS_TLS_PORT> (8443) con el certificado del tablero de Agora, firmado por la CA
en la que el runner ya confía: por la red viajan tokens, nunca en claro.

`python -m ai_os_core.serve`. Con AI_OS_OPEN_MONITOR=1 abre el monitor ya con el token del
director, sin pedirlo.
"""

import asyncio
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

import uvicorn

from .config import settings

LOOPBACK = {"127.0.0.1", "localhost", "::1"}


def _director_token() -> str:
    from .app import _load_tokens
    return next((t for t, g in _load_tokens().items() if g.principal is None), "")


def _open_monitor(port: int) -> None:
    url = f"http://127.0.0.1:{port}"
    for _ in range(120):  # espera a que conteste antes de abrir el navegador
        try:
            urllib.request.urlopen(url + "/health", timeout=1).close()
            break
        except OSError:
            time.sleep(0.5)
    token = _director_token()
    # El token va tras '#': el navegador no lo envía a ningún servidor; la página lo guarda y lo borra de la barra
    webbrowser.open(f"{url}/monitor" + (f"#token={token}" if token else ""))


def _proceso_en(port: int) -> str:
    """«nombre (PID n)» de quien escucha en el puerto, según netstat/tasklist de Windows."""
    try:
        lineas = subprocess.run(["netstat", "-ano", "-p", "TCP"], capture_output=True, text=True,
                                timeout=10).stdout.splitlines()
        pid = next(linea.split()[-1] for linea in lineas
                   if "LISTENING" in linea and linea.split()[1].endswith(f":{port}"))
        fila = subprocess.run(["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
                              capture_output=True, text=True, timeout=10).stdout.strip()
        return f"{fila.split(',')[0].strip(chr(34)) or 'proceso'} (PID {pid})"
    except (OSError, StopIteration, IndexError, subprocess.SubprocessError):
        return "otro programa"


def puerto_ocupado(port: int) -> str | None:
    """None si se puede escuchar en 127.0.0.1:port; si no, qué hacer, dicho para una persona."""
    with socket.socket() as prueba:
        try:
            prueba.bind(("127.0.0.1", port))
            return None
        except OSError:
            pass
    return (f"El puerto {port} de Core ya lo usa {_proceso_en(port)}. Ciérralo y vuelve a arrancar Core, "
            f"o arranca Core en otro con AI_OS_PORT (las apps toman el nuevo de su carpeta de conexión al "
            f"arrancar). Si es ComfyUI Desktop: su puerto es el 8188 y solo cae en el {port} cuando, al "
            "abrirse, encuentra el suyo ocupado; reinícialo después de arrancar Core.")


def main() -> int:
    from .app import _load_tokens, app

    port = settings.port
    motivo = puerto_ocupado(port)
    if motivo:
        print(motivo)
        return 1
    configs = [uvicorn.Config(app, host="127.0.0.1", port=port)]
    if settings.host not in LOOPBACK:
        if not _load_tokens():
            print("AI_OS_HOST abre Core a la red y no hay tokens (AI_OS_AUTO_TOKENS=false sin AI_OS_API_TOKEN): no se arranca.")
            return 1
        cert = Path(os.getenv("AI_OS_TLS_CERT", r"C:\Agora\pki\server.crt"))
        key = Path(os.getenv("AI_OS_TLS_KEY", r"C:\Agora\pki\server.key"))
        if not (cert.is_file() and key.is_file()):
            print(f"Para abrir Core a la red hace falta un certificado (no está {cert} o {key}).")
            print("Fija AI_OS_TLS_CERT/AI_OS_TLS_KEY o instala el tablero de Agora. Por la red no va nada en claro.")
            return 1
        tls_port = int(os.getenv("AI_OS_TLS_PORT", "8443"))
        # lifespan="off": la base ya la prepara el primer servidor; dos bootstrap a la vez competirían
        configs.append(uvicorn.Config(app, host=settings.host, port=tls_port, lifespan="off",
                                      ssl_certfile=str(cert), ssl_keyfile=str(key)))
        print(f"Red local: https://{settings.host}:{tls_port} (certificado {cert})")
    print(f"Este equipo: http://127.0.0.1:{port}")
    if os.getenv("AI_OS_OPEN_MONITOR") == "1":
        threading.Thread(target=_open_monitor, args=(port,), daemon=True).start()

    servers = [uvicorn.Server(c) for c in configs]

    async def serve_all() -> None:
        tasks = [asyncio.create_task(s.serve()) for s in servers]
        # Si uno se para (Ctrl+C o puerto ocupado), se paran todos
        await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for s in servers:
            s.should_exit = True
        await asyncio.gather(*tasks, return_exceptions=True)

    try:
        asyncio.run(serve_all())
    except KeyboardInterrupt:
        pass
    return 0 if all(s.started for s in servers) else 1  # p. ej. un puerto ya ocupado


if __name__ == "__main__":
    sys.exit(main())
