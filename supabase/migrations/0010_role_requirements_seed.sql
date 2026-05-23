-- Seed role requirements for standard UK construction job titles.
-- Looks up training_type IDs by name — no hardcoded UUIDs.
-- ON CONFLICT DO NOTHING: safe to re-run.

WITH t AS (SELECT id, name FROM training_types),

operative AS (
  SELECT 'Operative' AS job_title, t.id AS training_type_id FROM t
  WHERE t.name IN (
    'Company Induction', 'H&S Awareness For Operatives', 'CSCS Card',
    'Manual Handling Essentials', 'Operative H&S Touch Screen Test',
    'Fire Essentials for Construction Trades', 'Working @ Height Essentials',
    'Emergency First Aid at Work 1 Day'
  )
),
site_operative AS (
  SELECT 'Site Operative' AS job_title, t.id FROM t
  WHERE t.name IN (
    'Company Induction', 'H&S Awareness For Operatives', 'CSCS Card',
    'Manual Handling Essentials', 'Operative H&S Touch Screen Test',
    'Fire Essentials for Construction Trades', 'Working @ Height Essentials'
  )
),
supervisor AS (
  SELECT 'Supervisor' AS job_title, t.id FROM t
  WHERE t.name IN (
    'Company Induction', 'CSCS Card', 'Supervisors H&S Training',
    'Supervisors H&S Touch Screen Test', 'Manual Handling Essentials',
    'Risk Assessment', 'Working @ Height Essentials',
    'Fire Essentials for Construction Trades', 'Emergency First Aid at Work 1 Day'
  )
),
manager AS (
  SELECT 'Manager' AS job_title, t.id FROM t
  WHERE t.name IN (
    'Company Induction', 'CSCS Card', 'Managers H&S Training',
    'Managers H&S Touch Screen Test', 'Risk Assessment', 'CDM for Contractors',
    'First Aid at Work 3 Day', 'Waste Management Essentials',
    'Fire Essentials for Construction Trades'
  )
),
site_manager AS (
  SELECT 'Site Manager' AS job_title, t.id FROM t
  WHERE t.name IN (
    'Company Induction', 'CSCS Card', 'Managers H&S Training',
    'Managers H&S Touch Screen Test', 'Risk Assessment', 'CDM for Contractors',
    'First Aid at Work 3 Day', 'Working @ Height Essentials',
    'Fire Essentials for Construction Trades', 'Asbestos Essentials', 'COSHH Essentials'
  )
),
director AS (
  SELECT 'Director' AS job_title, t.id FROM t
  WHERE t.name IN (
    'Company Induction', 'Directors Role for H&S', 'Risk Assessment',
    'CDM for Contractors', 'First Aid at Work 3 Day', 'Waste Management Essentials'
  )
),

all_reqs AS (
  SELECT * FROM operative
  UNION ALL SELECT * FROM site_operative
  UNION ALL SELECT * FROM supervisor
  UNION ALL SELECT * FROM manager
  UNION ALL SELECT * FROM site_manager
  UNION ALL SELECT * FROM director
)
INSERT INTO role_requirements (job_title, training_type_id)
SELECT job_title, training_type_id FROM all_reqs
ON CONFLICT (job_title, training_type_id) DO NOTHING;
