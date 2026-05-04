from fastapi.testclient import TestClient

from app import database
from app.main import app


def test_health_blocks_and_character_pagination(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "app.sqlite3")

    with TestClient(app) as client:
        assert client.get("/api/health").json() == {"status": "ok"}

        blocks = client.get("/api/unicode/blocks").json()
        assert blocks

        response = client.get(f"/api/unicode/blocks/{blocks[0]['id']}/characters?page=1&page_size=8")
        assert response.status_code == 200
        payload = response.json()
        assert payload["page"] == 1
        assert payload["page_size"] == 8
        assert len(payload["items"]) == 8

