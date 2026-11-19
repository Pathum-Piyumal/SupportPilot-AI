# SupportPilot AI

A fictional banking support demo combining intent classification, evidence-grounded drafts, and human review. **Current status: project foundation plus a deterministic BANKING77 preparation pipeline.** Authentication, tickets, trained models, retrieval, drafting, and analytics are not implemented.

Project requirements: [masterplan](<MASTERPLAN (4).md>) and [proposal](<project proposal.md.txt>). Original planning files are preserved.

## Repository structure

```text
apps/web/       React + TypeScript + Vite app, routing and API client
apps/api/       FastAPI, configuration, health routes, Alembic and tests
ml/            Offline Python package; training dependencies are optional
knowledge/     Future fictional policies, retrieval fixtures and evaluations
data/          Local datasets (ignored by Git)
artifacts/     Local model artifacts (ignored by Git)
docs/          Architecture, decisions and progress
scripts/       Developer setup
.github/       CI and contributor templates
```

## Requirements

- Node.js 22.21.0 (pinned in `.node-version`) and npm.
- Python 3.12 and uv. `uv sync` can install Python 3.12 if absent.
- Docker Desktop with Linux containers for PostgreSQL and container-based setup.

JavaScript uses npm workspaces and `package-lock.json`; Python uses a uv workspace and `uv.lock`. Do not commit secrets, real customer data, datasets, or model binaries.

## Windows PowerShell

From the repository root:

```powershell
.\scripts\dev-setup.ps1
docker compose up -d postgres
uv run alembic -c apps/api/alembic.ini upgrade head
uv run uvicorn app.main:app --reload
```

In another terminal:

```powershell
npm run dev
```

## Linux / macOS

```bash
test -f .env || cp .env.example .env
npm ci
uv sync --all-packages --locked
docker compose up -d postgres
uv run alembic -c apps/api/alembic.ini upgrade head
uv run uvicorn app.main:app --reload
# In another terminal:
npm run dev
```

## Run everything in Docker

```sh
docker compose up --build -d
```

This starts PostgreSQL, applies the baseline migration, starts the API, and serves the web scaffold. Use either container mode or local mode to avoid port conflicts. The web container uses Vite's development server; this is not a production deployment configuration.

- Web: http://localhost:5173
- API documentation: http://localhost:8000/docs
- Liveness: http://localhost:8000/health/live
- Readiness: http://localhost:8000/health/ready

Readiness checks database connectivity only. No model or LLM adapter is implemented. `LLM_PROVIDER=fake` reserves the future test configuration and makes no provider calls. The initial migration creates the Alembic version table; product tables will be implemented with the database phase. The database image includes pgvector, but its extension and retrieval schema are not yet initialized.

## Validation

```sh
npm run lint
npm run typecheck
npm test
npm run build
npm run format:check
uv run ruff check .
uv run ruff format --check .
uv run mypy apps/api/app ml/src
uv run pytest
```

The database test is skipped unless `RUN_DB_TESTS=1`. After starting PostgreSQL and applying migrations, enable it in PowerShell with `$env:RUN_DB_TESTS='1'; uv run pytest`, or in bash with `RUN_DB_TESTS=1 uv run pytest`. CI runs it against an ephemeral database.

For later ML work, install optional training tools with `uv sync --all-packages --extra training`. No dataset or model downloads are part of normal setup.

Next implementation work follows the masterplan's ML baseline phase. Dataset terms must be verified before downloading or redistributing BANKING77; see [data/README.md](data/README.md). License selection remains an owner decision in [docs/license-decision.md](docs/license-decision.md). No remote repository, branch protection, or deployment has been configured.
