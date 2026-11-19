import os

import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.mark.skipif(
    os.getenv("RUN_DB_TESTS") != "1", reason="Set RUN_DB_TESTS=1 with PostgreSQL running"
)
def test_database_ready() -> None:
    assert TestClient(app).get("/health/ready").status_code == 200
