# PLAN FOR AGENTS

## 1. Project Overview

This project is a small web application for browsing, inspecting, copying, and checking Unicode characters.

The application should help users:

- browse Unicode characters by block and page;
- jump to a Unicode block or code point range;
- inspect details of a selected character;
- copy a character or its code point;
- configure fonts for different Unicode blocks;
- inspect font metadata and Unicode coverage;
- identify which characters are supported or missing in a given font.

The application is intended as a practical character finding and font coverage tool.

## 2. Technology Stack

Use the following stack:

| Layer | Technology |
|---|---|
| Front end | React |
| Back end | FastAPI |
| Database | SQLite |
| Font parsing | fontTools |
| Data format | Unicode metadata imported into SQLite or structured JSON |
| Local development | Simple local scripts or Docker Compose if needed |

The first version should remain lightweight and easy to run locally.

## 3. Core Design Principles

The system should be simple, transparent, and easy to extend.

Key principles:

1. Treat Unicode metadata and font coverage data as separate concerns.
2. Use server-side font parsing for reliable coverage detection.
3. Avoid rendering too many characters at once in the browser.
4. Make the selected character visually prominent.
5. Keep the UI focused on browsing, inspection, and copying.
6. Allow future extension to complex Unicode sequences, while the MVP focuses mainly on single code points.

## 4. Main Functional Modules

### 4.1 Unicode Browser

The Unicode browser is the main page.

It should support:

- Unicode block navigation;
- paged character grid;
- code point range browsing;
- character selection;
- large preview of the selected character;
- copy character button;
- copy code point button;
- display of basic character metadata.

The character grid should show each character and its code point.

Example:

```text
A
U+0041
```

The selected character should be shown in a larger display area.

### 4.2 Character Detail Panel

When a character is selected, show:

* character glyph;
* code point, for example `U+4E2D`;
* Unicode name;
* Unicode block;
* general category;
* script, if available;
* plane, if available;
* copy controls;
* font preview area.

The panel should also show whether the currently selected font supports the character.

### 4.3 Font Management

The font management module should support:

* uploading `.ttf`, `.otf`, and possibly `.woff2` files;
* listing registered fonts;
* viewing font metadata;
* deleting a font record;
* refreshing coverage data.

Use `fontTools.ttLib.TTFont` to inspect uploaded font files.

Store uploaded fonts in a local directory, and store metadata in SQLite.

### 4.4 Font Metadata Extraction

For each uploaded font, extract as much useful information as practical:

* family name;
* full font name;
* PostScript name;
* style;
* supported code points from the `cmap` table;
* total supported Unicode code point count;
* file format;
* file size;
* upload time.

The exact metadata available may vary by font file. Handle missing fields gracefully.

### 4.5 Font Coverage Analysis

The system should calculate coverage by Unicode block.

For a selected font and block, return:

* total code points in the block;
* number of supported code points;
* number of missing code points;
* coverage percentage;
* list of supported characters;
* list of missing characters.

Coverage should be based on the parsed font `cmap` table, not visual detection in the browser.

### 4.6 Font Configuration by Unicode Block

Allow users to configure preferred fonts for Unicode blocks.

Example configuration:

```json
{
  "Basic Latin": ["Inter", "Arial"],
  "CJK Unified Ideographs": ["Noto Sans CJK SC", "Source Han Sans SC"],
  "Mathematical Operators": ["STIX Two Math", "Cambria Math"],
  "Emoji": ["Noto Color Emoji", "Apple Color Emoji"]
}
```

The browser should use the configured font stack when rendering characters in a block.

## 5. Data Model

Use SQLite for local persistence.

Suggested tables:

### 5.1 unicode_blocks

Stores Unicode block definitions.

Fields:

* `id`
* `name`
* `start_codepoint`
* `end_codepoint`
* `plane`
* `sort_order`

### 5.2 unicode_characters

Stores character metadata.

Fields:

* `id`
* `codepoint`
* `char`
* `name`
* `block_id`
* `category`
* `script`
* `plane`

### 5.3 fonts

Stores uploaded font metadata.

Fields:

* `id`
* `family_name`
* `full_name`
* `postscript_name`
* `style`
* `file_path`
* `file_format`
* `file_size`
* `supported_codepoint_count`
* `created_at`

### 5.4 font_codepoints

Stores parsed font coverage.

Fields:

* `id`
* `font_id`
* `codepoint`

Add an index on:

```sql
(font_id, codepoint)
```

### 5.5 block_font_configs

Stores preferred fonts for Unicode blocks.

Fields:

* `id`
* `block_id`
* `font_id`
* `priority`

## 6. API Design

Use FastAPI.

Suggested endpoints:

### Unicode

```text
GET /api/unicode/blocks
GET /api/unicode/blocks/{block_id}/characters?page=1&page_size=256
GET /api/unicode/characters/{codepoint}
GET /api/unicode/search?q=...
```

### Fonts

```text
GET /api/fonts
POST /api/fonts/upload
GET /api/fonts/{font_id}
DELETE /api/fonts/{font_id}
GET /api/fonts/{font_id}/coverage
GET /api/fonts/{font_id}/coverage/{block_id}
```

### Font Configuration

```text
GET /api/font-config
PUT /api/font-config/{block_id}
```

## 7. Front-end Structure

Suggested React pages:

```text
/src/pages/UnicodeBrowser.tsx
/src/pages/FontManager.tsx
/src/pages/FontCoverage.tsx
/src/pages/Settings.tsx
```

Suggested components:

```text
/src/components/BlockNavigator.tsx
/src/components/CharacterGrid.tsx
/src/components/CharacterDetailPanel.tsx
/src/components/FontPreview.tsx
/src/components/FontUpload.tsx
/src/components/CoverageTable.tsx
/src/components/PaginationControls.tsx
```

The first version can combine several pages if this keeps the implementation simpler.

## 8. MVP Scope

The MVP should include:

1. Import Unicode block and character metadata.
2. Browse characters by Unicode block.
3. Page through characters.
4. Select a character and view details.
5. Copy character and code point.
6. Upload font files.
7. Parse font `cmap` data using fontTools.
8. Store font coverage in SQLite.
9. Display coverage for one font and one Unicode block.
10. Configure preferred fonts per Unicode block.

Do not include user accounts, cloud storage, collaborative features, or complex Unicode sequence handling in the MVP.

## 9. Implementation Milestones

### M1: Project Skeleton

Create:

* React front end;
* FastAPI back end;
* SQLite database;
* basic development scripts;
* health check endpoint.

Acceptance:

* front end starts locally;
* back end starts locally;
* database initialisation works.

### M2: Unicode Data Import

Create a script to import Unicode blocks and character metadata.

Acceptance:

* Unicode blocks can be listed through the API;
* characters can be queried by block;
* pagination works.

### M3: Character Browser

Implement the main browser UI.

Acceptance:

* user can select a block;
* characters are shown in a grid;
* user can page through characters;
* selected character is enlarged;
* copy buttons work.

### M4: Font Upload and Parsing

Implement font upload and metadata extraction.

Acceptance:

* user can upload a font;
* server extracts basic font metadata;
* server extracts supported Unicode code points;
* font record is stored in SQLite.

### M5: Coverage Checking

Implement coverage calculation.

Acceptance:

* user can select a font and Unicode block;
* application shows supported count, missing count, and percentage;
* supported and missing characters can be inspected.

### M6: Font Configuration

Implement block-level font configuration.

Acceptance:

* user can assign preferred fonts to Unicode blocks;
* character grid uses configured font stack;
* selected character preview uses the selected or configured font.

## 10. Important Technical Notes

Unicode code points should be stored as integers internally. Display them as uppercase hexadecimal strings, for example:

```text
U+0041
U+4E2D
U+1F600
```

When rendering characters in React, use JavaScript string conversion carefully:

```ts
String.fromCodePoint(codepoint)
```

Do not rely on browser visual rendering to decide font support. Browsers may silently use fallback fonts.

Font coverage should be determined from the font `cmap` table through `fontTools`.

The first version should focus on single code points. Complex Unicode sequences such as emoji ZWJ sequences, variation selectors, combining marks, and regional indicator pairs can be handled in later versions.

## 11. Testing Requirements

Add basic tests for:

* Unicode import script;
* code point conversion;
* block range query;
* font upload validation;
* `cmap` extraction;
* coverage percentage calculation;
* API pagination.

For front-end testing, at minimum verify:

* block list rendering;
* character grid rendering;
* character selection;
* copy button behaviour;
* font coverage display.

## 12. Suggested Directory Structure

```text
unicode-font-browser/
  backend/
    app/
      main.py
      database.py
      models.py
      schemas.py
      routers/
        unicode.py
        fonts.py
        font_config.py
      services/
        unicode_service.py
        font_service.py
        coverage_service.py
      scripts/
        import_unicode_data.py
    data/
      unicode/
      fonts/
    tests/
  frontend/
    src/
      pages/
      components/
      api/
      types/
      utils/
  README.md
  AGENTS.md
```

## 13. Final Delivery Target

The final MVP should let a user open the web app, choose a Unicode block, browse characters, inspect a selected character, copy it, upload a font, and check whether that font covers the selected block or character.

The application should be small, local-first, and reliable enough to serve as a useful Unicode and font inspection tool.

