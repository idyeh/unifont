from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query

from app.database import get_connection
from app.schemas import PaginatedCharacters, UnicodeBlock, UnicodeCharacter
from app.services import unicode_service

router = APIRouter(prefix="/api/unicode", tags=["unicode"])


@router.get("/blocks", response_model=list[UnicodeBlock])
def blocks() -> list[UnicodeBlock]:
    with get_connection() as connection:
        return unicode_service.list_blocks(connection)


@router.get("/blocks/{block_id}/characters", response_model=PaginatedCharacters)
def block_characters(
    block_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(256, ge=1, le=512),
) -> PaginatedCharacters:
    with get_connection() as connection:
        if not unicode_service.get_block(connection, block_id):
            raise HTTPException(status_code=404, detail="Unicode block not found.")
        return unicode_service.list_characters_for_block(connection, block_id, page, page_size)


@router.get("/characters/{codepoint}", response_model=UnicodeCharacter)
def character(codepoint: str) -> UnicodeCharacter:
    try:
        parsed = unicode_service.parse_codepoint(codepoint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    with get_connection() as connection:
        result = unicode_service.get_character(connection, parsed)
        if not result:
            raise HTTPException(status_code=404, detail="Unicode character not found.")
        return result


@router.get("/search", response_model=list[UnicodeCharacter])
def search(q: str = Query(..., min_length=1)) -> list[UnicodeCharacter]:
    with get_connection() as connection:
        return unicode_service.search_characters(connection, q)

