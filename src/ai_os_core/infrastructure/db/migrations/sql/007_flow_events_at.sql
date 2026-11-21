-- Auditoría 19-nov (A-11): la retención del monitor borra por fecha; sin índice recorría toda la tabla.
CREATE INDEX IF NOT EXISTS idx_flow_events_at ON flow_events (at);
