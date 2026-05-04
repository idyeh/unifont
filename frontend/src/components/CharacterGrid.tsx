import type { UnicodeCharacter } from "../types";

type Props = {
  characters: UnicodeCharacter[];
  selectedCodepoint?: number;
  fontStack?: string;
  onSelect: (character: UnicodeCharacter) => void;
};

export function CharacterGrid({ characters, selectedCodepoint, fontStack, onSelect }: Props) {
  return (
    <div className="character-grid">
      {characters.map((character) => (
        <button
          key={character.codepoint}
          className={character.codepoint === selectedCodepoint ? "character-cell active" : "character-cell"}
          onClick={() => onSelect(character)}
          style={{ fontFamily: fontStack }}
          title={character.name}
        >
          <span className="glyph">{character.char}</span>
          <span className="code">{character.display_codepoint}</span>
        </button>
      ))}
    </div>
  );
}

