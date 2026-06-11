-- Demo sandbox seed — fictional company for prospect demos.
-- Run on the SANDBOX Supabase project only, after migrations 0001-0013.
-- All expiry dates are relative to CURRENT_DATE so the demo never goes stale.
-- Wrapped in a DO block so it runs atomically in the Supabase SQL editor.

DO $$
DECLARE
    p_alan   uuid; p_beth   uuid; p_carl   uuid; p_dawn   uuid;
    p_eric   uuid; p_fiona  uuid; p_gary   uuid; p_holly  uuid;
BEGIN
    -- Wipe any previous demo data (people cascade to records)
    DELETE FROM training_records;
    DELETE FROM people;

    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Alan Briggs', 'Site Manager', true, CURRENT_DATE - INTERVAL '6 years', true)
    RETURNING id INTO p_alan;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Beth Connor', 'Groundworker', true, CURRENT_DATE - INTERVAL '3 years', true)
    RETURNING id INTO p_beth;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Carl Davies', 'Plant Operator', false, CURRENT_DATE - INTERVAL '4 years', true)
    RETURNING id INTO p_carl;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Dawn Ellis', 'Supervisor', true, CURRENT_DATE - INTERVAL '8 years', true)
    RETURNING id INTO p_dawn;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Eric Foster', 'Labourer', false, CURRENT_DATE - INTERVAL '1 year', true)
    RETURNING id INTO p_eric;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Fiona Grant', 'First Aider', true, CURRENT_DATE - INTERVAL '5 years', true)
    RETURNING id INTO p_fiona;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Gary Hughes', 'Scaffolder', false, CURRENT_DATE - INTERVAL '2 years', true)
    RETURNING id INTO p_gary;
    INSERT INTO people (name, job_title, paye, start_date, active)
    VALUES ('Holly Irwin', 'Site Administrator', true, CURRENT_DATE - INTERVAL '2 years', true)
    RETURNING id INTO p_holly;

    -- Records: mixed urgency so the dashboard, matrix, and timeline all look busy.
    -- Helper pattern: completed = expiry - typical validity.

    -- EXPIRED (red — drives the "act now" story)
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_beth, id, CURRENT_DATE - INTERVAL '5 years 20 days', CURRENT_DATE - INTERVAL '20 days'
    FROM training_types WHERE name ILIKE '%CSCS%' LIMIT 1;
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_eric, id, CURRENT_DATE - INTERVAL '3 years 10 days', CURRENT_DATE - INTERVAL '10 days'
    FROM training_types WHERE name ILIKE '%manual handling%' LIMIT 1;

    -- DUE WITHIN 7 DAYS (orange)
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_carl, id, CURRENT_DATE - INTERVAL '3 years' + INTERVAL '5 days', CURRENT_DATE + INTERVAL '5 days'
    FROM training_types WHERE name ILIKE '%IPAF%' OR name ILIKE '%plant%' LIMIT 1;

    -- DUE WITHIN 30 DAYS (amber)
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_fiona, id, CURRENT_DATE - INTERVAL '3 years' + INTERVAL '21 days', CURRENT_DATE + INTERVAL '21 days'
    FROM training_types WHERE name ILIKE '%first aid%' LIMIT 1;
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_gary, id, CURRENT_DATE - INTERVAL '2 years' + INTERVAL '28 days', CURRENT_DATE + INTERVAL '28 days'
    FROM training_types WHERE name ILIKE '%harness%' OR name ILIKE '%height%' LIMIT 1;

    -- DUE WITHIN 90 DAYS (blue)
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_alan, id, CURRENT_DATE - INTERVAL '5 years' + INTERVAL '70 days', CURRENT_DATE + INTERVAL '70 days'
    FROM training_types WHERE name ILIKE '%SMSTS%' OR name ILIKE '%site management%' LIMIT 1;
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p_dawn, id, CURRENT_DATE - INTERVAL '5 years' + INTERVAL '85 days', CURRENT_DATE + INTERVAL '85 days'
    FROM training_types WHERE name ILIKE '%SSSTS%' OR name ILIKE '%supervis%' LIMIT 1;

    -- IN DATE (green — the bulk, so the gauge isn't all red)
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p.pid, t.id, CURRENT_DATE - INTERVAL '6 months', CURRENT_DATE + INTERVAL '2 years 6 months'
    FROM (VALUES (p_alan), (p_carl), (p_dawn), (p_fiona), (p_gary), (p_holly)) AS p(pid)
    CROSS JOIN LATERAL (
        SELECT id FROM training_types
        WHERE name ILIKE '%asbestos%' OR name ILIKE '%awareness%'
        LIMIT 1
    ) t;
    INSERT INTO training_records (person_id, training_type_id, completed_date, expiry_date)
    SELECT p.pid, t.id, CURRENT_DATE - INTERVAL '1 year', CURRENT_DATE + INTERVAL '4 years'
    FROM (VALUES (p_alan), (p_dawn), (p_holly)) AS p(pid)
    CROSS JOIN LATERAL (
        SELECT id FROM training_types WHERE name ILIKE '%fire%' LIMIT 1
    ) t;

    -- Settings: demo sender identity, no real recipient
    UPDATE settings SET
        reminder_recipient_email = NULL,
        sender_name = 'Demo Construction Ltd';
END $$;
