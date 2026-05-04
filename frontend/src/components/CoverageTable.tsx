import type { BlockCoverage } from "../types";

type Props = {
  coverage?: BlockCoverage;
};

export function CoverageTable({ coverage }: Props) {
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
        <CharacterList title="Supported" characters={coverage.supported_characters} />
        <CharacterList title="Missing" characters={coverage.missing_characters} />
      </div>
    </section>
  );
}

function CharacterList({
  title,
  characters
}: {
  title: string;
  characters: BlockCoverage["supported_characters"];
}) {
  return (
    <div className="coverage-list">
      <div className="panel-title">{title}</div>
      <div className="mini-grid">
        {characters.slice(0, 120).map((character) => (
          <span key={character.codepoint} title={`${character.display_codepoint} ${character.name}`}>
            {character.char}
          </span>
        ))}
      </div>
    </div>
  );
}

