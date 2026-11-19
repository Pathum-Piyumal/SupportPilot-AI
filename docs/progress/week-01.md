# Week 01 — Project initialization

## Done

- Initialized a local Git repository and the planned web/API/ML folder structure.
- Added npm and uv workspaces, lockfiles, environment examples, and developer setup commands.
- Added React routing, a typed health client, FastAPI health routes, request IDs, and error responses.
- Added an Alembic baseline, development Compose configuration, CI, and contributor templates.
- Preserved the original planning documents; feature modules remain explicit placeholders.

## Evidence

- Backend: Ruff lint/format and mypy pass; four unit tests pass.
- Frontend: ESLint, TypeScript, Prettier, two render tests, and production build pass.
- Docker Compose configuration validates; Alembic generates baseline SQL successfully.
- Updated React Router, Vite, Vitest, and ESLint dependencies after the initial npm audit. Frontend checks pass again. A follow-up online audit did not finish; the offline audit reported zero advisories but does not establish a current online security result.
- Database integration test is skipped locally. The database image download was stopped due to slow network transfer; database migrations and full Docker startup remain unverified.

## Next

Complete database runtime verification, then follow the masterplan's dataset provenance and ML baseline work. CI is configured but has not run on a remote repository. Model training, RAG, authentication, and ticket workflows are not implemented.
