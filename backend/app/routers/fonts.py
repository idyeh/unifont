from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, Response, UploadFile, status

from app.database import get_connection
from app.schemas import BlockCoverage, FontCharacterSupport, FontDetail, FontSummary
from app.services import coverage_service, font_service, unicode_service

router = APIRouter(prefix="/api/fonts", tags=["fonts"])


@router.get("", response_model=list[FontSummary])
def fonts() -> list[FontSummary]:
    with get_connection() as connection:
        return font_service.list_fonts(connection)


@router.post("/upload", response_model=FontDetail)
def upload_font(file: UploadFile = File(...)) -> FontDetail:
    with get_connection() as connection:
        return font_service.save_uploaded_font(connection, file)


@router.get("/{font_id}", response_model=FontDetail)
def font(font_id: int) -> FontDetail:
    with get_connection() as connection:
        result = font_service.get_font(connection, font_id)
        if not result:
            raise HTTPException(status_code=404, detail="Font not found.")
        return result


@router.get("/{font_id}/characters/{codepoint}/support", response_model=FontCharacterSupport)
def character_support(font_id: int, codepoint: str) -> FontCharacterSupport:
    try:
        parsed = unicode_service.parse_codepoint(codepoint)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    with get_connection() as connection:
        supported = font_service.supports_codepoint(connection, font_id, parsed)
        if supported is None:
            raise HTTPException(status_code=404, detail="Font not found.")
        return FontCharacterSupport(
            font_id=font_id,
            codepoint=parsed,
            display_codepoint=unicode_service.format_codepoint(parsed),
            supported=supported,
        )


@router.delete("/{font_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
def delete_font(font_id: int) -> Response:
    with get_connection() as connection:
        if not font_service.delete_font(connection, font_id):
            raise HTTPException(status_code=404, detail="Font not found.")
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/{font_id}/coverage/{block_id}", response_model=BlockCoverage)
def block_coverage(font_id: int, block_id: int) -> BlockCoverage:
    with get_connection() as connection:
        result = coverage_service.calculate_block_coverage(connection, font_id, block_id)
        if not result:
            raise HTTPException(status_code=404, detail="Font or Unicode block not found.")
        return result
