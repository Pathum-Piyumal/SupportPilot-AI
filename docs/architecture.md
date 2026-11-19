# Architecture

React communicates with a FastAPI modular monolith. PostgreSQL is the persistent store; pgvector is planned for retrieval. Offline ML is a separate package. The scaffold implements health routes only; all workflow and ML/RAG capabilities remain planned.
