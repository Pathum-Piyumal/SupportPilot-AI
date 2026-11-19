from unittest.mock import MagicMock, patch

from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

client = TestClient(app)


def test_live() -> None:
    response = client.get("/health/live")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
    assert response.headers["X-Request-ID"]


def test_ready() -> None:
    with patch("app.api.v1.health.engine", MagicMock()):
        response = client.get("/health/ready")
    assert response.status_code == 200
    assert response.json() == {"status": "ready"}


def test_database_failure_redacts_connection_details() -> None:
    with patch(
        "app.api.v1.health.engine.connect", side_effect=OperationalError("secret", {}, Exception())
    ):
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert response.json()["error"]["message"] == "Database unavailable"
    assert "secret" not in response.text
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]


def test_unknown_route_has_error_envelope() -> None:
    response = client.get("/missing")
    assert response.status_code == 404
    assert response.json()["error"]["request_id"] == response.headers["X-Request-ID"]
