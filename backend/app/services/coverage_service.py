from __future__ import annotations

from sqlite3 import Connection

from app.schemas import BlockCoverage, CoverageCharacter, FontCoveragePage, FontCoveragePageCharacter
from app.services.unicode_service import (
    character_name,
    format_codepoint,
    get_block,
    list_characters_for_block,
    safe_character,
)


def _coverage_character(codepoint: int) -> CoverageCharacter:
    return CoverageCharacter(
        codepoint=codepoint,
        display_codepoint=format_codepoint(codepoint),
        char=safe_character(codepoint),
        name=character_name(codepoint),
    )


def calculate_block_coverage(
    connection: Connection, font_id: int, block_id: int, list_limit: int = 512
) -> BlockCoverage | None:
    block = get_block(connection, block_id)
    if not block:
        return None

    font_exists = connection.execute("SELECT 1 FROM fonts WHERE id = ?", (font_id,)).fetchone()
    if not font_exists:
        return None

    rows = connection.execute(
        """
        SELECT codepoint
        FROM font_codepoints
        WHERE font_id = ? AND codepoint BETWEEN ? AND ?
        ORDER BY codepoint
        """,
        (font_id, block.start_codepoint, block.end_codepoint),
    ).fetchall()
    supported = {row["codepoint"] for row in rows}
    block_codepoints = [
        codepoint
        for codepoint in range(block.start_codepoint, block.end_codepoint + 1)
        if not (0xD800 <= codepoint <= 0xDFFF)
    ]
    total = len(block_codepoints)
    supported_count = sum(1 for codepoint in block_codepoints if codepoint in supported)
    missing_count = total - supported_count
    percentage = round((supported_count / total * 100) if total else 0, 2)
    supported_list = [codepoint for codepoint in block_codepoints if codepoint in supported][:list_limit]
    missing_list = [codepoint for codepoint in block_codepoints if codepoint not in supported][:list_limit]

    return BlockCoverage(
        font_id=font_id,
        block_id=block_id,
        block_name=block.name,
        total_codepoints=total,
        supported_count=supported_count,
        missing_count=missing_count,
        coverage_percentage=percentage,
        supported_characters=[_coverage_character(codepoint) for codepoint in supported_list],
        missing_characters=[_coverage_character(codepoint) for codepoint in missing_list],
        list_limit=list_limit,
    )


def calculate_page_support(
    connection: Connection, font_id: int, block_id: int, page: int = 1, page_size: int = 128
) -> FontCoveragePage | None:
    block = get_block(connection, block_id)
    if not block:
        return None

    font_exists = connection.execute("SELECT 1 FROM fonts WHERE id = ?", (font_id,)).fetchone()
    if not font_exists:
        return None

    characters = list_characters_for_block(connection, block_id, page, page_size)
    if not characters.items:
        return FontCoveragePage(
            items=[],
            page=characters.page,
            page_size=characters.page_size,
            total=characters.total,
            total_pages=characters.total_pages,
        )

    first = min(character.codepoint for character in characters.items)
    last = max(character.codepoint for character in characters.items)
    rows = connection.execute(
        """
        SELECT codepoint
        FROM font_codepoints
        WHERE font_id = ? AND codepoint BETWEEN ? AND ?
        """,
        (font_id, first, last),
    ).fetchall()
    supported = {row["codepoint"] for row in rows}

    return FontCoveragePage(
        items=[
            FontCoveragePageCharacter(**character.model_dump(), supported=character.codepoint in supported)
            for character in characters.items
        ],
        page=characters.page,
        page_size=characters.page_size,
        total=characters.total,
        total_pages=characters.total_pages,
    )
