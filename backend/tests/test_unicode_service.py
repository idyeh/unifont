import sqlite3

from app.database import SCHEMA
from app.services.coverage_service import calculate_block_coverage
from app.services.unicode_service import format_codepoint, list_characters_for_block, seed_unicode_data


def memory_connection():
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    connection.executescript(SCHEMA)
    return connection


def test_format_codepoint_uses_uppercase_unicode_style():
    assert format_codepoint(0x41) == "U+0041"
    assert format_codepoint(0x1F600) == "U+1F600"


def test_seed_data_supports_block_pagination():
    connection = memory_connection()
    seed_unicode_data(connection)
    page = list_characters_for_block(connection, 1, page=1, page_size=16)
    assert page.total == 128
    assert page.total_pages == 8
    assert page.items[0].display_codepoint == "U+0000"


def test_coverage_percentage_for_basic_latin_subset():
    connection = memory_connection()
    seed_unicode_data(connection)
    cursor = connection.execute(
        """
        INSERT INTO fonts(family_name, full_name, postscript_name, style, file_path, file_format, file_size, supported_codepoint_count)
        VALUES ('Demo', 'Demo Regular', 'Demo-Regular', 'Regular', '/tmp/demo.ttf', 'ttf', 2, 2)
        """
    )
    font_id = cursor.lastrowid
    connection.executemany(
        "INSERT INTO font_codepoints(font_id, codepoint) VALUES (?, ?)",
        [(font_id, 0x41), (font_id, 0x42)],
    )
    connection.commit()

    coverage = calculate_block_coverage(connection, font_id, 1)
    assert coverage is not None
    assert coverage.total_codepoints == 128
    assert coverage.supported_count == 2
    assert coverage.coverage_percentage == 1.56
