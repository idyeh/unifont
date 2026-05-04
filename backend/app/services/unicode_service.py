from __future__ import annotations

import math
import unicodedata
from pathlib import Path
from sqlite3 import Connection, Row

from app.schemas import PaginatedCharacters, UnicodeBlock, UnicodeCharacter

UNICODE_DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "unicode"

FALLBACK_BLOCKS = [
    ("Basic Latin", 0x0000, 0x007F),
    ("Latin-1 Supplement", 0x0080, 0x00FF),
    ("Latin Extended-A", 0x0100, 0x017F),
    ("IPA Extensions", 0x0250, 0x02AF),
    ("Spacing Modifier Letters", 0x02B0, 0x02FF),
    ("Combining Diacritical Marks", 0x0300, 0x036F),
    ("Greek and Coptic", 0x0370, 0x03FF),
    ("Cyrillic", 0x0400, 0x04FF),
    ("Hebrew", 0x0590, 0x05FF),
    ("Arabic", 0x0600, 0x06FF),
    ("Devanagari", 0x0900, 0x097F),
    ("Thai", 0x0E00, 0x0E7F),
    ("Hiragana", 0x3040, 0x309F),
    ("Katakana", 0x30A0, 0x30FF),
    ("CJK Unified Ideographs", 0x4E00, 0x9FFF),
    ("Hangul Syllables", 0xAC00, 0xD7AF),
    ("General Punctuation", 0x2000, 0x206F),
    ("Superscripts and Subscripts", 0x2070, 0x209F),
    ("Currency Symbols", 0x20A0, 0x20CF),
    ("Letterlike Symbols", 0x2100, 0x214F),
    ("Number Forms", 0x2150, 0x218F),
    ("Arrows", 0x2190, 0x21FF),
    ("Mathematical Operators", 0x2200, 0x22FF),
    ("Box Drawing", 0x2500, 0x257F),
    ("Block Elements", 0x2580, 0x259F),
    ("Geometric Shapes", 0x25A0, 0x25FF),
    ("Miscellaneous Symbols", 0x2600, 0x26FF),
    ("Dingbats", 0x2700, 0x27BF),
    ("Emoticons", 0x1F600, 0x1F64F),
    ("Miscellaneous Symbols and Pictographs", 0x1F300, 0x1F5FF),
    ("Supplemental Symbols and Pictographs", 0x1F900, 0x1F9FF),
]


def format_codepoint(codepoint: int) -> str:
    return f"U+{codepoint:04X}"


def parse_codepoint(value: str) -> int:
    normalized = value.strip().upper().replace("U+", "")
    if normalized.startswith("0X"):
        normalized = normalized[2:]
    codepoint = int(normalized, 16)
    if codepoint < 0 or codepoint > 0x10FFFF:
        raise ValueError("Code point is outside Unicode range.")
    return codepoint


def plane_for_codepoint(codepoint: int) -> str:
    plane = codepoint >> 16
    names = {
        0: "Basic Multilingual Plane",
        1: "Supplementary Multilingual Plane",
        2: "Supplementary Ideographic Plane",
        3: "Tertiary Ideographic Plane",
        14: "Supplementary Special-purpose Plane",
        15: "Supplementary Private Use Area-A",
        16: "Supplementary Private Use Area-B",
    }
    return names.get(plane, f"Plane {plane}")


def character_name(codepoint: int) -> str:
    try:
        return unicodedata.name(chr(codepoint))
    except ValueError:
        category = unicodedata.category(chr(codepoint))
        if category == "Cc":
            return f"<control-{format_codepoint(codepoint)}>"
        return "<unassigned>"


def safe_character(codepoint: int) -> str:
    if 0xD800 <= codepoint <= 0xDFFF:
        return "\uFFFD"
    return chr(codepoint)


def row_to_block(row: Row) -> UnicodeBlock:
    return UnicodeBlock(**dict(row))


def row_to_character(row: Row) -> UnicodeCharacter:
    data = dict(row)
    data["display_codepoint"] = format_codepoint(data["codepoint"])
    return UnicodeCharacter(**data)


def seed_unicode_data(connection: Connection) -> None:
    existing = connection.execute("SELECT COUNT(*) FROM unicode_blocks").fetchone()[0]
    if existing:
        return

    for sort_order, (name, start, end) in enumerate(sorted(FALLBACK_BLOCKS, key=lambda item: item[1]), start=1):
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
            characters.append(
                (
                    codepoint,
                    char,
                    character_name(codepoint),
                    block_id,
                    unicodedata.category(char),
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


def list_blocks(connection: Connection) -> list[UnicodeBlock]:
    rows = connection.execute(
        """
        SELECT id, name, start_codepoint, end_codepoint, plane, sort_order
        FROM unicode_blocks
        ORDER BY sort_order, start_codepoint
        """
    ).fetchall()
    return [row_to_block(row) for row in rows]


def get_block(connection: Connection, block_id: int) -> UnicodeBlock | None:
    row = connection.execute(
        """
        SELECT id, name, start_codepoint, end_codepoint, plane, sort_order
        FROM unicode_blocks
        WHERE id = ?
        """,
        (block_id,),
    ).fetchone()
    return row_to_block(row) if row else None


def list_characters_for_block(
    connection: Connection, block_id: int, page: int = 1, page_size: int = 256
) -> PaginatedCharacters:
    page = max(page, 1)
    page_size = min(max(page_size, 1), 512)
    total = connection.execute(
        "SELECT COUNT(*) FROM unicode_characters WHERE block_id = ?", (block_id,)
    ).fetchone()[0]
    offset = (page - 1) * page_size
    rows = connection.execute(
        """
        SELECT c.id, c.codepoint, c.char, c.name, c.block_id, b.name AS block_name,
               c.category, c.script, c.plane
        FROM unicode_characters c
        JOIN unicode_blocks b ON b.id = c.block_id
        WHERE c.block_id = ?
        ORDER BY c.codepoint
        LIMIT ? OFFSET ?
        """,
        (block_id, page_size, offset),
    ).fetchall()
    return PaginatedCharacters(
        items=[row_to_character(row) for row in rows],
        page=page,
        page_size=page_size,
        total=total,
        total_pages=max(1, math.ceil(total / page_size)) if total else 1,
    )


def get_character(connection: Connection, codepoint: int) -> UnicodeCharacter | None:
    row = connection.execute(
        """
        SELECT c.id, c.codepoint, c.char, c.name, c.block_id, b.name AS block_name,
               c.category, c.script, c.plane
        FROM unicode_characters c
        JOIN unicode_blocks b ON b.id = c.block_id
        WHERE c.codepoint = ?
        """,
        (codepoint,),
    ).fetchone()
    if row:
        return row_to_character(row)

    if codepoint < 0 or codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
        return None
    char = safe_character(codepoint)
    return UnicodeCharacter(
        codepoint=codepoint,
        display_codepoint=format_codepoint(codepoint),
        char=char,
        name=character_name(codepoint),
        category=unicodedata.category(char),
        plane=plane_for_codepoint(codepoint),
    )


def search_characters(connection: Connection, query: str, limit: int = 50) -> list[UnicodeCharacter]:
    query = query.strip()
    if not query:
        return []
    params: list[object]
    where: str
    try:
        codepoint = parse_codepoint(query)
        where = "c.codepoint = ?"
        params = [codepoint]
    except ValueError:
        where = "c.name LIKE ? OR b.name LIKE ?"
        params = [f"%{query.upper()}%", f"%{query}%"]

    rows = connection.execute(
        f"""
        SELECT c.id, c.codepoint, c.char, c.name, c.block_id, b.name AS block_name,
               c.category, c.script, c.plane
        FROM unicode_characters c
        JOIN unicode_blocks b ON b.id = c.block_id
        WHERE {where}
        ORDER BY c.codepoint
        LIMIT ?
        """,
        (*params, limit),
    ).fetchall()
    return [row_to_character(row) for row in rows]
