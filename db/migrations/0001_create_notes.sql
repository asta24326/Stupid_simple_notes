-- Baseline: the schema that db/init.sql used to create
-- IF NOT EXISTS lets this file also run on a database created before migrations existed.
CREATE TABLE IF NOT EXISTS notes (
    id SERIAL PRIMARY KEY,
    text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);