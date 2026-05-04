from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class UnicodeBlock(BaseModel):
    id: int
    name: str
    start_codepoint: int
    end_codepoint: int
    plane: str
    sort_order: int


class UnicodeCharacter(BaseModel):
    id: Optional[int] = None
    codepoint: int
    display_codepoint: str
    char: str
    name: str
    block_id: Optional[int] = None
    block_name: Optional[str] = None
    category: str
    script: Optional[str] = None
    plane: str


class PaginatedCharacters(BaseModel):
    items: list[UnicodeCharacter]
    page: int
    page_size: int
    total: int
    total_pages: int


class FontSummary(BaseModel):
    id: int
    family_name: Optional[str]
    full_name: Optional[str]
    postscript_name: Optional[str]
    style: Optional[str]
    file_format: str
    file_size: int
    supported_codepoint_count: int
    created_at: str


class FontDetail(FontSummary):
    file_path: str


class FontCharacterSupport(BaseModel):
    font_id: int
    codepoint: int
    display_codepoint: str
    supported: bool


class CoverageCharacter(BaseModel):
    codepoint: int
    display_codepoint: str
    char: str
    name: str


class BlockCoverage(BaseModel):
    font_id: int
    block_id: int
    block_name: str
    total_codepoints: int
    supported_count: int
    missing_count: int
    coverage_percentage: float
    supported_characters: list[CoverageCharacter]
    missing_characters: list[CoverageCharacter]
    list_limit: int = Field(description="Maximum number of supported or missing characters returned.")


class FontConfigEntry(BaseModel):
    block_id: int
    block_name: str
    fonts: list[FontSummary]


class FontConfigUpdate(BaseModel):
    font_ids: list[int]
