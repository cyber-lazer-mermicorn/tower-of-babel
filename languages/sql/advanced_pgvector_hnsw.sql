-- Advanced exhibit: tenant-isolated vector evidence store patterns.
-- HNSW-style retrieval sketch, RLS, constraints, bounded search.
-- Requires PostgreSQL + pgvector in real environments (service_gated).

-- Canonical state
CREATE TABLE IF NOT EXISTS mission_receipts (
  id            UUID PRIMARY KEY,
  tenant_id     UUID NOT NULL,
  mission_id    TEXT NOT NULL,
  embedding     VECTOR(384),
  payload       JSONB NOT NULL DEFAULT '{}',
  created_at    TIMESTAMPTZ NOT NULL DEFAULT now(),
  CONSTRAINT mission_receipts_tenant_mission UNIQUE (tenant_id, mission_id)
);

-- Example index (pgvector)
-- CREATE INDEX IF NOT EXISTS mission_receipts_embedding_hnsw
--   ON mission_receipts USING hnsw (embedding vector_cosine_ops);

-- Row level security sketch
ALTER TABLE mission_receipts ENABLE ROW LEVEL SECURITY;

-- Bounded search function sketch (service must supply real vector ops)
-- CREATE OR REPLACE FUNCTION search_receipts(
--   p_tenant UUID,
--   p_query VECTOR(384),
--   p_limit INT DEFAULT 10
-- ) RETURNS SETOF mission_receipts
-- LANGUAGE sql STABLE AS $$
--   SELECT * FROM mission_receipts
--   WHERE tenant_id = p_tenant
--   ORDER BY embedding <=> p_query
--   LIMIT LEAST(GREATEST(p_limit, 1), 50);
-- $$;

-- This file is intentionally a contract + pattern exhibit.
-- Full execution requires a live Postgres + pgvector service.
