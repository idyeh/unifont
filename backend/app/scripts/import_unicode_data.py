from __future__ import annotations

import csv
import unicodedata
from pathlib import Path

from app.database import get_connection, init_db
from app.services.unicode_service import (
    FALLBACK_BLOCKS,
    UNICODE_DATA_DIR,
    character_name,
    plane_for_codepoint,
    safe_character,
    seed_unicode_data,
)


def _read_blocks(path: Path) -> list[tuple[str, int, int]]:
    if not path.exists():
        return FALLBACK_BLOCKS
    blocks: list[tuple[str, int, int]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].strip()
        if not line:
            continue
        code_range, name = [part.strip() for part in line.split(";", 1)]
        start_hex, end_hex = code_range.split("..")
        blocks.append((name, int(start_hex, 16), int(end_hex, 16)))
    return blocks


def _read_unicode_names(path: Path) -> dict[int, tuple[str, str]]:
    if not path.exists():
        return {}
    names: dict[int, tuple[str, str]] = {}
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.reader(handle, delimiter=";")
        for row in reader:
            if len(row) >= 3:
                names[int(row[0], 16)] = (row[1], row[2])
    return names


def import_unicode_data() -> None:
    init_db()
    blocks_path = UNICODE_DATA_DIR / "Blocks.txt"
    unicode_data_path = UNICODE_DATA_DIR / "UnicodeData.txt"
    blocks = _read_blocks(blocks_path)
    names = _read_unicode_names(unicode_data_path)

    with get_connection() as connection:
        connection.execute("DELETE FROM block_font_configs")
        connection.execute("DELETE FROM unicode_characters")
        connection.execute("DELETE FROM unicode_blocks")

        if not blocks_path.exists() and not unicode_data_path.exists():
            seed_unicode_data(connection)
            return

        for sort_order, (name, start, end) in enumerate(blocks, start=1):
            cursor = connection.execute(
                """
                INSERT INTO unicode_blocks(name, start_codepoint, end_codepoint, plane, sort_order)
                VALUES (?, ?, ?, ?, ?)
                """,
                (name, start, end, plane_for_codepoint(start), sort_order),
            )
            block_id = cursor.lastrowid
            characters = []
            for codepoint in range(start, end + 1):
                if 0xD800 <= codepoint <= 0xDFFF:
                    continue
                char = safe_character(codepoint)
                imported_name, imported_category = names.get(
                    codepoint, (character_name(codepoint), unicodedata.category(char))
                )
                characters.append(
                    (
                        codepoint,
                        char,
                        imported_name,
                        block_id,
                        imported_category,
                        None,
                        plane_for_codepoint(codepoint),
                    )
                )
            connection.executemany(
                """
                INSERT INTO unicode_characters(codepoint, char, name, block_id, category, script, plane)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                characters,
            )
        connection.commit()


if __name__ == "__main__":
    import_unicode_data()

