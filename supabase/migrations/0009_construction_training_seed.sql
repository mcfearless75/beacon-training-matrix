-- Seed standard UK construction H&S training types with categories
-- Safe to re-run: ON CONFLICT updates category only
INSERT INTO training_types (name, category, active) VALUES
  ('Company Induction',                      'Core H&S',          true),
  ('H&S Awareness For Operatives',           'Core H&S',          true),
  ('H&S Awareness for Office Staff',         'Core H&S',          true),
  ('Risk Assessment',                        'Core H&S',          true),
  ('CDM for Contractors',                    'Core H&S',          true),
  ('Operative H&S Touch Screen Test',        'Core H&S',          true),
  ('Supervisors H&S Touch Screen Test',      'Core H&S',          true),
  ('Managers H&S Touch Screen Test',         'Core H&S',          true),
  ('Waste Management Essentials',            'Core H&S',          true),
  ('Directors Role for H&S',                 'Role Specific',     true),
  ('Managers H&S Training',                  'Role Specific',     true),
  ('Supervisors H&S Training',               'Role Specific',     true),
  ('First Aid at Work 3 Day',                'First Aid',         true),
  ('Emergency First Aid at Work 1 Day',      'First Aid',         true),
  ('Asbestos Essentials',                    'Site Operations',   true),
  ('COSHH Essentials',                       'Site Operations',   true),
  ('Manual Handling Essentials',             'Site Operations',   true),
  ('Working @ Height Essentials',            'Site Operations',   true),
  ('Safe Use of Ladders & Steps',            'Site Operations',   true),
  ('Fire Essentials for Construction Trades','Site Operations',   true),
  ('Abrasive Wheels',                        'Site Operations',   true),
  ('CSCS Card',                              'Plant & Equipment', true),
  ('Safe Use of Tower Scaffolds PASMA',      'Plant & Equipment', true),
  ('IPAF Powered Access',                    'Plant & Equipment', true)
ON CONFLICT (name) DO UPDATE SET category = EXCLUDED.category, active = true;

-- Patch any pre-existing types that landed in General
UPDATE training_types SET category = 'First Aid'         WHERE name ILIKE '%first aid%'       AND category = 'General';
UPDATE training_types SET category = 'Plant & Equipment' WHERE name ILIKE '%ipaf%'            AND category = 'General';
UPDATE training_types SET category = 'Site Operations'   WHERE name ILIKE '%manual handling%' AND category = 'General';
UPDATE training_types SET category = 'Core H&S'          WHERE name ILIKE '%induction%'       AND category = 'General';
UPDATE training_types SET category = 'Plant & Equipment' WHERE name ILIKE '%cscs%'            AND category = 'General';
