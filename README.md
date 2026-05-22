# Beacon Training Matrix

Internal training expiry tracker for Beacon Risk. See `docs/superpowers/specs/` for the design.

## Local dev
1. Copy `.env.example` to `.env` and fill in
2. `python -m venv .venv && .venv\Scripts\activate`
3. `pip install -e ".[dev]"`
4. `streamlit run app/streamlit_app.py`

## Cron (daily reminders)
`python -m cron.run_reminders`
