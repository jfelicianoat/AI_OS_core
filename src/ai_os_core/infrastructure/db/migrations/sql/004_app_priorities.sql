-- Migración 004: prioridad de cada app en la cola del AI Broker (Client_API §5.1.1)
-- La fija el director desde el monitor; Core la devuelve al evaluar `<app>:broker` y la app
-- la manda como `priority` (0–1000, menor = antes). Sin fila, la app no la manda (100 del Broker).

CREATE TABLE IF NOT EXISTS app_priorities (
    app TEXT PRIMARY KEY,
    priority INTEGER NOT NULL CHECK (priority BETWEEN 0 AND 1000),
    updated_at TEXT NOT NULL
);
