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


def test_font_coverage_page_marks_visible_support(tmp_path, monkeypatch):
    monkeypatch.setattr(database, "DB_PATH", tmp_path / "app.sqlite3")

    with TestClient(app) as client:
        with database.get_connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO fonts(
                    family_name, full_name, postscript_name, style, file_path,
                    file_format, file_size, supported_codepoint_count
                )
                VALUES ('Demo', 'Demo Regular', 'Demo-Regular', 'Regular', '/tmp/demo.ttf', 'ttf', 2, 1)
                """
            )
            font_id = cursor.lastrowid
            connection.execute(
                "INSERT INTO font_codepoints(font_id, codepoint) VALUES (?, ?)",
                (font_id, 0x0000),
            )
            connection.commit()

        response = client.get(f"/api/fonts/{font_id}/coverage/1/characters?page=1&page_size=2")
        assert response.status_code == 200
        payload = response.json()
        assert [item["supported"] for item in payload["items"]] == [True, False]
