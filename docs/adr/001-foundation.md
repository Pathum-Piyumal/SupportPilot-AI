# ADR 001: Repository foundation

Status: accepted

Use the masterplan's modular monolith with apps/web, apps/api, and ml. Use npm workspaces for the frontend and a uv workspace for Python, with committed lockfiles. Python is 3.12; Node is pinned in .node-version. Training dependencies are optional to keep normal API development lightweight. Start with plain CSS; defer UI tooling until feature implementation. Domain modules are placeholders, not completed features.
