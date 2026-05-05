import type { BlockCoverage, CoverageCharacter } from "../types";

type Props = {
  coverage?: BlockCoverage;
  onCharacterSelect?: (character: CoverageCharacter) => void;
};

export function CoverageTable({ coverage, onCharacterSelect }: Props) {
  if (!coverage) {
    return <div className="empty-state compact">Upload or select a font to inspect coverage.</div>;
  }

  return (
    <section className="coverage">
      <div className="coverage-stats">
        <div>
          <strong>{coverage.coverage_percentage}%</strong>
          <span>covered</span>
        </div>
        <div>
          <strong>{coverage.supported_count}</strong>
          <span>supported</span>
        </div>
        <div>
          <strong>{coverage.missing_count}</strong>
          <span>missing</span>
        </div>
      </div>
      <div className="coverage-lists">
        <CharacterList
          title="Supported sample"
          characters={coverage.supported_characters}
          onCharacterSelect={onCharacterSelect}
        />
        <CharacterList
          title="Missing sample"
          characters={coverage.missing_characters}
          onCharacterSelect={onCharacterSelect}
        />
      </div>
    </section>
  );
}

function CharacterList({
  title,
  characters,
  onCharacterSelect
}: {
  title: string;
  characters: BlockCoverage["supported_characters"];
  onCharacterSelect?: (character: CoverageCharacter) => void;
}) {
  return (
    <div className="coverage-list">
      <div className="panel-title">{title}</div>
      <div className="mini-grid">
        {characters.slice(0, 120).map((character) => (
          <button
            key={character.codepoint}
            title={`${character.display_codepoint} ${character.name}`}
            onClick={() => onCharacterSelect?.(character)}
          >
            {character.char}
          </button>
        ))}
      </div>
    </div>
  );
}
