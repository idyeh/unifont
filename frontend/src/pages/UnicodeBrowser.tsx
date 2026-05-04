import { useEffect, useState } from "react";
import { api } from "../api/client";
import { BlockNavigator } from "../components/BlockNavigator";
import { CharacterDetailPanel } from "../components/CharacterDetailPanel";
import { CharacterGrid } from "../components/CharacterGrid";
import { CoverageTable } from "../components/CoverageTable";
import { FontUpload } from "../components/FontUpload";
import { PaginationControls } from "../components/PaginationControls";
import type { BlockCoverage, FontSummary, PaginatedCharacters, UnicodeBlock, UnicodeCharacter } from "../types";
import { fontLabel } from "../utils/codepoint";

export function UnicodeBrowser() {
  const [blocks, setBlocks] = useState<UnicodeBlock[]>([]);
  const [selectedBlock, setSelectedBlock] = useState<UnicodeBlock>();
  const [characters, setCharacters] = useState<PaginatedCharacters>();
  const [selectedCharacter, setSelectedCharacter] = useState<UnicodeCharacter>();
  const [page, setPage] = useState(1);
  const [fonts, setFonts] = useState<FontSummary[]>([]);
  const [selectedFontId, setSelectedFontId] = useState<number>();
  const [coverage, setCoverage] = useState<BlockCoverage>();
  const [fontSupportsCharacter, setFontSupportsCharacter] = useState<boolean>();
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
      .characters(selectedBlock.id, page)
      .then((result) => {
        setCharacters(result);
        setSelectedCharacter((current) => current ?? result.items[0]);
      })
      .catch((err: Error) => setError(err.message));
  }, [selectedBlock, page]);

  useEffect(() => {
    if (!selectedBlock || !selectedFontId) {
      setCoverage(undefined);
      return;
    }
    void api
      .coverage(selectedFontId, selectedBlock.id)
      .then(setCoverage)
      .catch((err: Error) => setError(err.message));
  }, [selectedBlock, selectedFontId]);

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
  const fontStack = selectedFont ? `"${fontLabel(selectedFont)}", system-ui, sans-serif` : undefined;

  async function uploadFont(file: File) {
    const font = await api.uploadFont(file);
    const nextFonts = await api.fonts();
    setFonts(nextFonts);
    setSelectedFontId(font.id);
  }

  return (
    <main className="app-shell">
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
              {characters && (
                <PaginationControls page={characters.page} totalPages={characters.total_pages} onPageChange={setPage} />
              )}
            </div>
            <CharacterGrid
              characters={characters?.items ?? []}
              selectedCodepoint={selectedCharacter?.codepoint}
              fontStack={fontStack}
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
            <CoverageTable coverage={coverage} />
          </aside>
        </div>
      </section>
    </main>
  );
}
