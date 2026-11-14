-- La caducidad de claves de idempotencia borra por fecha en cada reserva.
CREATE INDEX IF NOT EXISTS idx_idempotency_created_at ON idempotency_keys (created_at);
