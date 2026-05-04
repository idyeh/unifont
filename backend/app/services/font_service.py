from __future__ import annotations

import os
import shutil
import uuid
from pathlib import Path
from sqlite3 import Connection, Row

from fastapi import HTTPException, UploadFile
from fontTools.ttLib import TTFont

from app.schemas import FontDetail, FontSummary

FONT_DIR = Path(os.getenv("UNICODE_FONT_DIR", Path(__file__).resolve().parents[2] / "data" / "fonts"))
ALLOWED_EXTENSIONS = {".ttf", ".otf", ".woff2"}


def validate_font_filename(filename: str) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        allowed = ", ".join(sorted(ALLOWED_EXTENSIONS))
        raise HTTPException(status_code=400, detail=f"Font must be one of: {allowed}")
    return suffix


def row_to_font_summary(row: Row) -> FontSummary:
    data = dict(row)
    data.pop("file_path", None)
    return FontSummary(**data)


def row_to_font_detail(row: Row) -> FontDetail:
    return FontDetail(**dict(row))


def _best_name(font: TTFont, name_id: int) -> str | None:
    if "name" not in font:
        return None
    candidates = font["name"].names
    for record in candidates:
        if record.nameID == name_id and record.platformID in {0, 3}:
            try:
                return record.toUnicode()
            except UnicodeDecodeError:
                continue
    for record in candidates:
        if record.nameID == name_id:
            try:
                return record.toUnicode()
            except UnicodeDecodeError:
                continue
    return None


def extract_font_data(path: Path) -> tuple[dict[str, object], set[int]]:
    try:
        font = TTFont(path, lazy=True)
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Unable to read font file: {exc}") from exc

    try:
        codepoints: set[int] = set()
        if "cmap" in font:
            for cmap_table in font["cmap"].tables:
                if cmap_table.isUnicode():
                    codepoints.update(
                        cp
                        for cp in cmap_table.cmap.keys()
                        if 0 <= cp <= 0x10FFFF and not (0xD800 <= cp <= 0xDFFF)
                    )
        metadata = {
            "family_name": _best_name(font, 1),
            "style": _best_name(font, 2),
            "full_name": _best_name(font, 4),
            "postscript_name": _best_name(font, 6),
            "file_format": path.suffix.lower().lstrip(".") or str(font.sfntVersion),
            "file_size": path.stat().st_size,
            "supported_codepoint_count": len(codepoints),
        }
        return metadata, codepoints
    finally:
        font.close()


def save_uploaded_font(connection: Connection, upload: UploadFile) -> FontDetail:
    suffix = validate_font_filename(upload.filename or "")
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    target = FONT_DIR / f"{uuid.uuid4().hex}{suffix}"
    with target.open("wb") as handle:
        shutil.copyfileobj(upload.file, handle)

    try:
        metadata, codepoints = extract_font_data(target)
        cursor = connection.execute(
            """
            INSERT INTO fonts(
                family_name, full_name, postscript_name, style, file_path, file_format,
                file_size, supported_codepoint_count
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                metadata["family_name"],
                metadata["full_name"],
                metadata["postscript_name"],
                metadata["style"],
                str(target),
                metadata["file_format"],
                metadata["file_size"],
                metadata["supported_codepoint_count"],
            ),
        )
        font_id = cursor.lastrowid
        connection.executemany(
            "INSERT OR IGNORE INTO font_codepoints(font_id, codepoint) VALUES (?, ?)",
            ((font_id, codepoint) for codepoint in sorted(codepoints)),
        )
        connection.commit()
    except Exception:
        target.unlink(missing_ok=True)
        raise

    font = get_font(connection, font_id)
    assert font is not None
    return font


def list_fonts(connection: Connection) -> list[FontSummary]:
    rows = connection.execute(
        """
        SELECT id, family_name, full_name, postscript_name, style, file_path, file_format,
               file_size, supported_codepoint_count, created_at
        FROM fonts
        ORDER BY created_at DESC, id DESC
        """
    ).fetchall()
    return [row_to_font_summary(row) for row in rows]


def get_font(connection: Connection, font_id: int) -> FontDetail | None:
    row = connection.execute(
        """
        SELECT id, family_name, full_name, postscript_name, style, file_path, file_format,
               file_size, supported_codepoint_count, created_at
        FROM fonts
        WHERE id = ?
        """,
        (font_id,),
    ).fetchone()
    return row_to_font_detail(row) if row else None


def delete_font(connection: Connection, font_id: int) -> bool:
    font = get_font(connection, font_id)
    if not font:
        return False
    connection.execute("DELETE FROM fonts WHERE id = ?", (font_id,))
    connection.commit()
    Path(font.file_path).unlink(missing_ok=True)
    return True


def supports_codepoint(connection: Connection, font_id: int, codepoint: int) -> bool | None:
    font_exists = connection.execute("SELECT 1 FROM fonts WHERE id = ?", (font_id,)).fetchone()
    if not font_exists:
        return None
    row = connection.execute(
        "SELECT 1 FROM font_codepoints WHERE font_id = ? AND codepoint = ?",
        (font_id, codepoint),
    ).fetchone()
    return row is not None
