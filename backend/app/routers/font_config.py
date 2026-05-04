from __future__ import annotations

from fastapi import APIRouter, HTTPException

from app.database import get_connection
from app.schemas import FontConfigEntry, FontConfigUpdate
from app.services.font_service import row_to_font_summary
from app.services.unicode_service import get_block

router = APIRouter(prefix="/api/font-config", tags=["font-config"])


@router.get("", response_model=list[FontConfigEntry])
def font_config() -> list[FontConfigEntry]:
    with get_connection() as connection:
        blocks = connection.execute(
            "SELECT id, name FROM unicode_blocks ORDER BY sort_order, start_codepoint"
        ).fetchall()
        entries: list[FontConfigEntry] = []
        for block in blocks:
            fonts = connection.execute(
                """
                SELECT f.id, f.family_name, f.full_name, f.postscript_name, f.style,
                       f.file_path, f.file_format, f.file_size,
                       f.supported_codepoint_count, f.created_at
                FROM block_font_configs c
                JOIN fonts f ON f.id = c.font_id
                WHERE c.block_id = ?
                ORDER BY c.priority, f.family_name
                """,
                (block["id"],),
            ).fetchall()
            entries.append(
                FontConfigEntry(
                    block_id=block["id"],
                    block_name=block["name"],
                    fonts=[row_to_font_summary(font) for font in fonts],
                )
            )
        return entries


@router.put("/{block_id}", response_model=FontConfigEntry)
def update_font_config(block_id: int, payload: FontConfigUpdate) -> FontConfigEntry:
    with get_connection() as connection:
        block = get_block(connection, block_id)
        if not block:
            raise HTTPException(status_code=404, detail="Unicode block not found.")
        if payload.font_ids:
            placeholders = ",".join("?" for _ in payload.font_ids)
            found = connection.execute(
                f"SELECT COUNT(*) FROM fonts WHERE id IN ({placeholders})", tuple(payload.font_ids)
            ).fetchone()[0]
            if found != len(set(payload.font_ids)):
                raise HTTPException(status_code=400, detail="One or more font ids are invalid.")

        connection.execute("DELETE FROM block_font_configs WHERE block_id = ?", (block_id,))
        connection.executemany(
            """
            INSERT INTO block_font_configs(block_id, font_id, priority)
            VALUES (?, ?, ?)
            """,
            ((block_id, font_id, priority) for priority, font_id in enumerate(payload.font_ids)),
        )
        connection.commit()

        fonts = connection.execute(
            """
            SELECT f.id, f.family_name, f.full_name, f.postscript_name, f.style,
                   f.file_path, f.file_format, f.file_size,
                   f.supported_codepoint_count, f.created_at
            FROM block_font_configs c
            JOIN fonts f ON f.id = c.font_id
            WHERE c.block_id = ?
            ORDER BY c.priority
            """,
            (block_id,),
        ).fetchall()
        return FontConfigEntry(
            block_id=block.id,
            block_name=block.name,
            fonts=[row_to_font_summary(font) for font in fonts],
        )

