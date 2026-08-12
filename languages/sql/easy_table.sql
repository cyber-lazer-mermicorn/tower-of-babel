-- Easy exhibit: minimal table. Teaches schema basics only.
CREATE TABLE IF NOT EXISTS tower_items (
  id   SERIAL PRIMARY KEY,
  name TEXT NOT NULL
);
