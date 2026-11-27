-- Soft delete: a note is deleted whe this column holds a time, alive while it is NULL
ALTER TABLE notes ADD COLUMN deleted_at TIMESTAMPTZ;

-- syntax:
-- ALTER TABLE - adjust existing table