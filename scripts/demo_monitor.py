"""Hace pasar por Core tres peticiones de ejemplo para ver el monitor en marcha.

No inventa nada que Core no haga: las autorizaciones son evaluaciones reales de política,
los recibos son recibos reales y los saltos se informan igual que lo harán las apps.
Lo único simulado es que las apps no están: el guion habla en su nombre.

  1. ChatyGPT -> Athena -> (Core autoriza) -> Broker -> Athena -> ChatyGPT
  2. Gestión Tareas IA -> Agora -> (Core deniega: dato restricted)
  3. una app que Core no tiene registrada (vision_lab) llama al Broker

Uso: python scripts/demo_monitor.py <core_url> [pausa_s]
Token común en AI_OS_API_TOKEN si Core lo exige. Antes, sembrar_ecosistema.py para tener políticas.
"""
import json
import os
import sys
import time
import urllib.request
import uuid

CORE = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8000"
PAUSA = float(sys.argv[2]) if len(sys.argv) > 2 else 1.4
TOKEN = os.environ.get("AI_OS_API_TOKEN")


def post(path, body, quien):
    headers = {"Content-Type": "application/json", "X-Principal-Id": quien}
    if TOKEN:
        headers["Authorization"] = f"Bearer {TOKEN}"
    req = urllib.request.Request(CORE + path, json.dumps(body).encode(), headers, method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())


def salto(flow, origen, destino, tipo, resumen="", **detalles):
    post("/api/v1/flows/hops", {"flow_id": flow, "source_system": origen, "target_system": destino,
                                "kind": tipo, "summary": resumen, "details": detalles}, origen)
    time.sleep(PAUSA)


def autorizar(flow, app, clasificacion):
    d = post("/api/v1/policies/evaluate", {"scope": f"{app}:broker", "principal_id": app,
                                           "context": {"data_classification": clasificacion, "flow_id": flow}}, app)
    if not d["matched_policy_refs"]:
        print(f"  [aviso] {app}:broker no tiene políticas: ejecuta antes scripts/sembrar_ecosistema.py")
    time.sleep(PAUSA)
    return d["authorization"] == "ALLOW" and d["executable"]


def recibo(flow, app, estado):
    post("/api/v1/operations/receipts", {"operation_id": f"op_{uuid.uuid4().hex[:10]}", "receiver_service": "ai_broker",
                                         "status": estado, "evidence": {"flow_id": flow}}, app)
    time.sleep(PAUSA)


def main():
    f1 = f"demo_{uuid.uuid4().hex[:8]}"
    print("1) ChatyGPT pide a Athena un resumen; Athena usa el Broker con permiso de Core")
    salto(f1, "chatygpt", "athena", "request", "resumen del informe de deriva")
    if autorizar(f1, "athena", "internal"):
        salto(f1, "athena", "ai_broker", "request", "tarea de resumen", model="gemma4:12b")
        salto(f1, "athena", "ai_broker", "response", "resultado", model="gemma4:12b", latency_ms=3240)
        recibo(f1, "athena", "succeeded")
        salto(f1, "chatygpt", "athena", "response", "respuesta entregada", latency_ms=5900)

    f2 = f"demo_{uuid.uuid4().hex[:8]}"
    print("2) Gestión Tareas IA deja trabajo en Agora con un dato restringido; Core lo para")
    salto(f2, "gestion_tareas", "agora", "request", "tarjeta: clasificar contratos")
    if not autorizar(f2, "agora", "restricted"):
        salto(f2, "gestion_tareas", "agora", "error", "core_denied")

    f3 = f"demo_{uuid.uuid4().hex[:8]}"
    print("3) Llega una app nueva que Core no tiene registrada")
    salto(f3, "vision_lab", "ai_broker", "request", "describir imagen")
    salto(f3, "vision_lab", "ai_broker", "response", "descripción", model="llava:13b", latency_ms=2100)
    print(f"Listo. Abre {CORE}/monitor")


if __name__ == "__main__":
    main()
