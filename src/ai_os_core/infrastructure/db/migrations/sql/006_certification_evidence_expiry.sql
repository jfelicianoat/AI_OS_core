-- AOS-06: una certificación puede atarse a su evidencia (sha256) y caducar.
-- Las dos son opcionales: las filas existentes quedan con NULL y se comportan igual que antes.
ALTER TABLE certification_applicability ADD COLUMN evidence_sha256 TEXT;
ALTER TABLE certification_applicability ADD COLUMN expires_at TEXT;
