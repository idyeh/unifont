from __future__ import annotations

import os
import sqlite3
from pathlib import Path

BACKEND_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = BACKEND_ROOT / "data"
DEFAULT_DB_PATH = DATA_DIR / "app.sqlite3"
DB_PATH = Path(os.getenv("UNICODE_BROWSER_DB", DEFAULT_DB_PATH))


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS unicode_blocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    start_codepoint INTEGER NOT NULL,
    end_codepoint INTEGER NOT NULL,
    plane TEXT NOT NULL,
    sort_order INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS unicode_characters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codepoint INTEGER NOT NULL UNIQUE,
    char TEXT NOT NULL,
    name TEXT NOT NULL,
    block_id INTEGER NOT NULL REFERENCES unicode_blocks(id) ON DELETE CASCADE,
    category TEXT NOT NULL,
    script TEXT,
    plane TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_unicode_characters_block_codepoint
ON unicode_characters(block_id, codepoint);

CREATE TABLE IF NOT EXISTS fonts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    family_name TEXT,
    full_name TEXT,
    postscript_name TEXT,
    style TEXT,
    file_path TEXT NOT NULL,
    file_format TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    supported_codepoint_count INTEGER NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS font_codepoints (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    font_id INTEGER NOT NULL REFERENCES fonts(id) ON DELETE CASCADE,
    codepoint INTEGER NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_font_codepoints_unique
ON font_codepoints(font_id, codepoint);

CREATE INDEX IF NOT EXISTS idx_font_codepoints_lookup
ON font_codepoints(font_id, codepoint);

CREATE TABLE IF NOT EXISTS block_font_configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    block_id INTEGER NOT NULL REFERENCES unicode_blocks(id) ON DELETE CASCADE,
    font_id INTEGER NOT NULL REFERENCES fonts(id) ON DELETE CASCADE,
    priority INTEGER NOT NULL,
    UNIQUE(block_id, font_id)
);

CREATE INDEX IF NOT EXISTS idx_block_font_configs_block
ON block_font_configs(block_id, priority);
"""


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(SCHEMA)

