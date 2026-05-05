import { useEffect, useState } from "react";
import { api } from "../api/client";
import { BlockNavigator } from "../components/BlockNavigator";
import { CharacterDetailPanel } from "../components/CharacterDetailPanel";
import { CharacterGrid } from "../components/CharacterGrid";
import { CoverageTable } from "../components/CoverageTable";
import { FontUpload } from "../components/FontUpload";
import { PaginationControls } from "../components/PaginationControls";
import type {
  BlockCoverage,
  CoverageCharacter,
  FontSummary,
  PaginatedCharacters,
  UnicodeBlock,
  UnicodeCharacter
} from "../types";
import { fontLabel, formatCodepoint } from "../utils/codepoint";

const PAGE_SIZE = 128;

function parseCodepointInput(value: string): number | undefined {
  const normalized = value.trim().toUpperCase().replace(/^U\+/, "").replace(/^0X/, "");
  if (!/^[0-9A-F]+$/.test(normalized)) {
    return undefined;
  }
  const codepoint = Number.parseInt(normalized, 16);
  return Number.isFinite(codepoint) && codepoint >= 0 && codepoint <= 0x10ffff ? codepoint : undefined;
}

export function UnicodeBrowser() {
  const [blocks, setBlocks] = useState<UnicodeBlock[]>([]);
  const [selectedBlock, setSelectedBlock] = useState<UnicodeBlock>();
  const [characters, setCharacters] = useState<PaginatedCharacters>();
  const [selectedCharacter, setSelectedCharacter] = useState<UnicodeCharacter>();
  const [page, setPage] = useState(1);
  const [fonts, setFonts] = useState<FontSummary[]>([]);
  const [selectedFontId, setSelectedFontId] = useState<number>();
  const [coverage, setCoverage] = useState<BlockCoverage>();
  const [supportByCodepoint, setSupportByCodepoint] = useState<Map<number, boolean>>();
  const [fontSupportsCharacter, setFontSupportsCharacter] = useState<boolean>();
  const [jumpInput, setJumpInput] = useState("");
  const [pendingJumpCodepoint, setPendingJumpCodepoint] = useState<number>();
  const [error, setError] = useState<string>();

  useEffect(() => {
    void api
      .blocks()
      .then((items) => {
        setBlocks(items);
        setSelectedBlock(items[0]);
      })
      .catch((err: Error) => setError(err.message));
    void api.fonts().then(setFonts).catch(() => setFonts([]));
  }, []);

  useEffect(() => {
    if (!selectedBlock) {
      return;
    }
    setPage(1);
  }, [selectedBlock?.id]);

  useEffect(() => {
    if (!selectedBlock) {
      return;
    }
    void api
      .characters(selectedBlock.id, page, PAGE_SIZE)
      .then((result) => {
        setCharacters(result);
        setSelectedCharacter((current) => {
          if (pendingJumpCodepoint !== undefined) {
            return result.items.find((item) => item.codepoint === pendingJumpCodepoint) ?? result.items[0];
          }
          if (current && result.items.some((item) => item.codepoint === current.codepoint)) {
            return current;
          }
          return result.items[0];
        });
        setPendingJumpCodepoint(undefined);
      })
      .catch((err: Error) => setError(err.message));
  }, [selectedBlock, page, pendingJumpCodepoint]);

  useEffect(() => {
    if (!selectedBlock || !selectedFontId) {
      setCoverage(undefined);
      return;
    }
    setCoverage(undefined);
    void api
      .coverage(selectedFontId, selectedBlock.id)
      .then(setCoverage)
      .catch((err: Error) => setError(err.message));
  }, [selectedBlock, selectedFontId]);

  useEffect(() => {
    if (!selectedBlock || !selectedFontId) {
      setSupportByCodepoint(undefined);
      return;
    }
    setSupportByCodepoint(undefined);
    void api
      .coveragePage(selectedFontId, selectedBlock.id, page, PAGE_SIZE)
      .then((result) => {
        setSupportByCodepoint(new Map(result.items.map((item) => [item.codepoint, item.supported])));
      })
      .catch((err: Error) => setError(err.message));
  }, [selectedBlock, selectedFontId, page]);

  useEffect(() => {
    if (!selectedFontId || !selectedCharacter) {
      setFontSupportsCharacter(undefined);
      return;
    }
    void api
      .characterSupport(selectedFontId, selectedCharacter.display_codepoint)
      .then((result) => setFontSupportsCharacter(result.supported))
      .catch(() => setFontSupportsCharacter(undefined));
  }, [selectedFontId, selectedCharacter]);

  const selectedFont = fonts.find((font) => font.id === selectedFontId);
  const selectedFontFace = selectedFont ? `uploaded-font-${selectedFont.id}` : undefined;
  const fontStack = selectedFont
    ? `"${selectedFontFace}", "${fontLabel(selectedFont)}", system-ui, sans-serif`
    : undefined;

  async function uploadFont(file: File) {
    const font = await api.uploadFont(file);
    const nextFonts = await api.fonts();
    setFonts(nextFonts);
    setSelectedFontId(font.id);
  }

  function jumpToCodepoint() {
    if (!selectedBlock) {
      return;
    }
    const codepoint = parseCodepointInput(jumpInput);
    if (codepoint === undefined) {
      setError("Enter a hexadecimal code point such as U+4E2D.");
      return;
    }
    navigateToCodepoint(codepoint);
  }

  function navigateToCodepoint(codepoint: number) {
    if (!selectedBlock) {
      return;
    }
    if (codepoint < selectedBlock.start_codepoint || codepoint > selectedBlock.end_codepoint) {
      setError(`${formatCodepoint(codepoint)} is outside ${selectedBlock.name}.`);
      return;
    }
    setJumpInput(formatCodepoint(codepoint));
    setPendingJumpCodepoint(codepoint);
    setPage(Math.floor((codepoint - selectedBlock.start_codepoint) / PAGE_SIZE) + 1);
  }

  function navigateToCoverageCharacter(character: CoverageCharacter) {
    navigateToCodepoint(character.codepoint);
  }

  return (
    <main className="app-shell">
      {selectedFont && selectedFontFace && (
        <style>{`
          @font-face {
            font-family: "${selectedFontFace}";
            src: url("${api.fontFileUrl(selectedFont.id)}");
            font-display: block;
          }
        `}</style>
      )}
      <BlockNavigator
        blocks={blocks}
        selectedBlockId={selectedBlock?.id}
        onSelect={(block) => {
          setSelectedBlock(block);
          setSelectedCharacter(undefined);
        }}
      />
      <section className="browser">
        <header className="topbar">
          <div>
            <h1>Unicode Font Browser</h1>
            <p>{selectedBlock ? `${selectedBlock.name} · ${selectedBlock.plane}` : "Loading blocks"}</p>
          </div>
          <div className="font-tools">
            <select
              value={selectedFontId ?? ""}
              onChange={(event) => setSelectedFontId(event.target.value ? Number(event.target.value) : undefined)}
              aria-label="Selected font"
            >
              <option value="">No font selected</option>
              {fonts.map((font) => (
                <option key={font.id} value={font.id}>
                  {fontLabel(font)}
                </option>
              ))}
            </select>
            <FontUpload onUpload={uploadFont} />
          </div>
        </header>
        {error && (
          <button className="error" onClick={() => setError(undefined)}>
            {error}
          </button>
        )}
        <div className="workspace">
          <section className="grid-panel">
            <div className="grid-toolbar">
              <span>{characters?.total ?? 0} code points</span>
              <div className="jump-control">
                <input
                  value={jumpInput}
                  onChange={(event) => setJumpInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter") {
                      jumpToCodepoint();
                    }
                  }}
                  placeholder="U+4E2D"
                  aria-label="Jump to code point"
                />
                <button onClick={jumpToCodepoint}>Go</button>
              </div>
              {characters && (
                <PaginationControls page={characters.page} totalPages={characters.total_pages} onPageChange={setPage} />
              )}
            </div>
            <CharacterGrid
              characters={characters?.items ?? []}
              selectedCodepoint={selectedCharacter?.codepoint}
              fontStack={fontStack}
              supportByCodepoint={supportByCodepoint}
              onSelect={setSelectedCharacter}
            />
          </section>
          <aside className="side-panels">
            <CharacterDetailPanel
              character={selectedCharacter}
              selectedFont={selectedFont}
              fontSupportsCharacter={fontSupportsCharacter}
              fontStack={fontStack}
            />
            <CoverageTable coverage={coverage} onCharacterSelect={navigateToCoverageCharacter} />
          </aside>
        </div>
      </section>
    </main>
  );
}
