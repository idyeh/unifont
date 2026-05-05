import type { UnicodeCharacter } from "../types";

type Props = {
  characters: UnicodeCharacter[];
  selectedCodepoint?: number;
  fontStack?: string;
  supportByCodepoint?: Map<number, boolean>;
  onSelect: (character: UnicodeCharacter) => void;
};

export function CharacterGrid({ characters, selectedCodepoint, fontStack, supportByCodepoint, onSelect }: Props) {
  return (
    <div className="character-grid">
      {characters.map((character) => {
        const support = supportByCodepoint?.get(character.codepoint);
        const classes = [
          "character-cell",
          character.codepoint === selectedCodepoint ? "active" : "",
          support === false ? "unsupported" : "",
          support === true ? "supported" : ""
        ]
          .filter(Boolean)
          .join(" ");

        return (
          <button
            key={character.codepoint}
            className={classes}
            onClick={() => onSelect(character)}
            style={{ fontFamily: fontStack }}
            title={`${character.name}${support === false ? " · missing from selected font" : ""}`}
          >
            <span className="glyph">{character.char}</span>
            <span className="code">{character.display_codepoint}</span>
          </button>
        );
      })}
    </div>
  );
}
