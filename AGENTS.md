# Repository Guidelines

## Project Structure & Module Organization
- `app/` houses the FastAPI service; `main.py` defines HTTP entrypoints, `helpers/` contains shared constants and data cleaning utilities, `services/` wraps AppFolio and Supabase integrations.
- `docs/` collects domain knowledge and API research; skim `docs/developer-advice-doc.md` before touching data contracts.
- `sandbox/` contains standalone scripts for exploratory calls to AppFolio and Supabase; use them for manual verification rather than production automation.
- `requirements.txt` tracks runtime dependencies; freeze updates with the same format when adding packages.

## Build, Test, and Development Commands
- `python -m venv venv && source venv/bin/activate` creates and activates a local virtual environment.
- `pip install -r requirements.txt` installs FastAPI, Supabase SDK, and supporting libraries.
- `uvicorn app.main:app --reload` starts the REST API for local testing on `http://127.0.0.1:8000`.
- `python sandbox/appfolio_test.py` exercises a full AppFolio fetch; prefer running from an activated venv with valid credentials.

## Coding Style & Naming Conventions
- Follow standard Python style: 4-space indentation, snake_case functions, and UpperCamelCase classes; constants belong in uppercase within `helpers/constants.py`.
- Group imports as stdlib, third-party, then local modules.
- Use type hints where practical and keep responses JSON-serializable.
- Avoid scattering environment lookups; centralize configuration in service modules and reuse helpers like `clean_record`.

## Testing Guidelines
- Automated tests rely on the sandbox scripts today; ensure every change keeps `python sandbox/*_test.py` runnable without modification.
- When adding formal tests, place them under `tests/` and use `pytest`; name files `test_<feature>.py` and include sample payload fixtures.
- Document any external API stubs or mocked Supabase tables in `docs/RESULTS.md` to maintain traceability.

## Commit & Pull Request Guidelines
- Commits follow Conventional Commit prefixes (`feat:`, `fix:`, `chore:`) as seen in `git log`; keep scopes small and descriptive.
- Every PR should include: a concise summary, linked issue or ticket, validation notes (commands run, datasets touched), and screenshots or JSON snippets when data structures change.
- Flag any migrations or environment variable additions in the PR description and update `docs/` if new knowledge is uncovered.

## Security & Configuration Tips
- Store credentials in `.env` (`APPFOLIO_CLIENT_ID`, `APPFOLIO_CLIENT_SECRET`, `V1_BASE_URL`, `V2_BASE_URL`, `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`); never commit secrets or print them in logs.
- Rotate keys before sharing screen recordings, and scrub sample outputs in docs to remove PII.
- Keep network calls wrapped with sensible timeouts (see `services/appfolio.py`), and verify Supabase writes through `update_supabase_details` before expanding table coverage.
