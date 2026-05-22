CREATE TABLE IF NOT EXISTS role_requirements (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  job_title text NOT NULL,
  training_type_id uuid NOT NULL REFERENCES training_types(id) ON DELETE CASCADE,
  created_at timestamptz DEFAULT now(),
  UNIQUE(job_title, training_type_id)
);
ALTER TABLE role_requirements ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Service role full access" ON role_requirements FOR ALL USING (true) WITH CHECK (true);
