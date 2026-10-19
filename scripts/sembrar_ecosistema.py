"""Deja Core listo para dirigir las apps del TFM: una política base por app.

Cada app, antes de mandar trabajo al AI Broker, evalúa en Core la política de su ámbito
(`<app>:broker`) y sólo envía con un ALLOW ejecutable. Sin políticas en el ámbito Core no
puede decidir y la app no envía nada (falla cerrado). Este guion crea, por ámbito:
  - DENY si `data_classification` es `restricted` (lo restringido no sale de su app);
  - ALLOW base sin condiciones.
Una app que no declare `data_classification` recibe INDETERMINATE: tampoco envía.

Uso: python sembrar_ecosistema.py <core_url>   (AI_OS_API_TOKEN en el entorno si Core lo exige;
ha de ser el token común, sin identidad: crea políticas de todas las apps).
Se puede repetir: las políticas llevan id fijo y se reescriben con la misma revisión.
"""
import os
import sys

import httpx

#: principal (token por app) -> ámbito de políticas que gobierna lo que manda al Broker
AMBITOS = {
    "gestion_tareas": "gestion_tareas:broker",
    "model_drift": "model_drift:broker",
    "athena": "athena:broker",
    "agora": "agora:broker",
    "knowledge_orchestrator": "knowledge_orchestrator:broker",
    "local_ai_lab": "local_ai_lab:broker",
    "trading_ai": "trading_ai:broker",
    "chatygpt": "chatygpt:broker",
}


def main() -> int:
    core = sys.argv[1].rstrip("/")
    token = os.environ.get("AI_OS_API_TOKEN")
    client = httpx.Client(base_url=core, timeout=10,
                          headers={"Authorization": f"Bearer {token}"} if token else {})
    for app, scope in AMBITOS.items():
        for body in (
            {"policy_id": f"eco_{app}_restringido", "policy_key": f"{app}_restringido_no_sale", "scope": scope,
             "decision_if_matched": "DENY",
             "conditions": [{"field": "data_classification", "operator": "in", "value": ["restricted", "RESTRICTED"]}]},
            {"policy_id": f"eco_{app}_base", "policy_key": f"{app}_base", "scope": scope,
             "decision_if_matched": "ALLOW", "unconditional": True},
        ):
            r = client.post("/api/v1/policies", json=body)
            if r.status_code not in (200, 201):
                print(f"[FALLO] {body['policy_id']}: {r.status_code} {r.text[:200]}")
                return 1
        ok = client.post("/api/v1/policies/evaluate", json={"scope": scope, "context": {"data_classification": "internal"}}).json()
        print(f"[OK] {scope}: internal -> {ok['authorization']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
