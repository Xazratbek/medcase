# Repository Guidelines

## Project Structure & Module Organization
- `ilova/`, `servislar/`, `marshrutlar/`, `modellar/`, `sxemalar/`: FastAPI backend (services, routes, ORM models, schemas).
- `frontend/`: Vite + React UI.
- `middleware/`, `yordamchilar/`, `vositalar/`, `sozlamalar/`: middleware, helpers, utilities, config.
- `migratsiyalar/`: Alembic migrations.
- `testlar/` and `tests/`: pytest unit tests + load tests (`tests/load_test/`).
- `nginx.conf`, `nginx.vps.conf`, `Dockerfile`, `docker-compose*.yml`: deployment and container setup.

## Build, Test, and Development Commands
- Backend deps: `pip install -r talablar.txt`
- Run backend (dev): `uvicorn ilova.asosiy:ilova --reload` or `./ishga_tushirish.sh`
- Run with Docker (all services): `docker compose up --build`
- Frontend dev: `cd frontend && npm install && npm run dev`
- Frontend build: `cd frontend && npm run build`

## Coding Style & Naming Conventions
- Python: 4-space indentation, PEP 8 style. Use Uzbek domain terms consistent with existing modules (e.g., `holat`, `rivojlanish`, `foydalanuvchi`).
- Frontend: 2-space indentation, camelCase for variables/functions, PascalCase for React components.
- Filenames follow existing Uzbek module naming (e.g., `rivojlanish_servisi.py`).

## Testing Guidelines
- Framework: `pytest`.
- Run all tests: `pytest`.
- Test files live in `testlar/` and `tests/` and follow `test_*.py` naming.
- Load tests: `tests/load_test/locustfile.py` (run via `locust` if needed).

## Commit & Pull Request Guidelines
- Git history shows informal, short subject lines (e.g., “new updates”). No strict convention enforced.
- Preferred: concise present-tense subjects (e.g., “Fix export stats”).
- PRs: include a brief description, test notes, and screenshots for UI changes when relevant.

## Security & Configuration Notes
- Environment config lives in `.env` (see `.env.namuna`).
- Avoid committing secrets; use env vars for DB, Redis, and JWT keys.
- Ignore generated folders like `node_modules/`, `venv/`, and `migratsiyalar/versiyalar/` when reviewing changes.
