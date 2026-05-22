ALTER TABLE training_types ADD COLUMN IF NOT EXISTS category text NOT NULL DEFAULT 'General';
