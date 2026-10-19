-- Migración 003: registro de flujos para el monitor visual (/monitor)
-- Cada fila es un paso de una petición que recorre el ecosistema: un salto entre apps
-- que la propia app informa, o una decisión/recibo que Core anota al recibirlos.
-- Sólo metadatos: nunca el texto de la petición ni de la respuesta.

CREATE TABLE IF NOT EXISTS flow_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    flow_id TEXT NOT NULL,
    at TEXT NOT NULL,
    kind TEXT NOT NULL,
    source TEXT NOT NULL,
    target TEXT NOT NULL,
    summary TEXT NOT NULL DEFAULT '',
    details_json TEXT NOT NULL DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_flow_events_flow ON flow_events(flow_id, id);
