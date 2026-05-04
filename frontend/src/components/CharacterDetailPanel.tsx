import { Copy } from "lucide-react";
import type { FontSummary, UnicodeCharacter } from "../types";
import { fontLabel } from "../utils/codepoint";

type Props = {
  character?: UnicodeCharacter;
  selectedFont?: FontSummary;
  fontSupportsCharacter?: boolean;
  fontStack?: string;
};

async function copyText(value: string) {
  await navigator.clipboard.writeText(value);
}

export function CharacterDetailPanel({
  character,
  selectedFont,
  fontSupportsCharacter,
  fontStack
}: Props) {
  if (!character) {
    return (
      <section className="detail-panel">
        <div className="empty-state">Select a character</div>
      </section>
    );
  }

  return (
    <section className="detail-panel">
      <div className="large-glyph" style={{ fontFamily: fontStack }}>
        {character.char}
      </div>
      <div className="detail-actions">
        <button onClick={() => copyText(character.char)}>
          <Copy size={16} />
          Character
        </button>
        <button onClick={() => copyText(character.display_codepoint)}>
          <Copy size={16} />
          Code point
        </button>
      </div>
      <dl className="metadata">
        <div>
          <dt>Code point</dt>
          <dd>{character.display_codepoint}</dd>
        </div>
        <div>
          <dt>Name</dt>
          <dd>{character.name}</dd>
        </div>
        <div>
          <dt>Block</dt>
          <dd>{character.block_name ?? "Unknown"}</dd>
        </div>
        <div>
          <dt>Category</dt>
          <dd>{character.category}</dd>
        </div>
        <div>
          <dt>Plane</dt>
          <dd>{character.plane}</dd>
        </div>
        <div>
          <dt>Font support</dt>
          <dd>
            {selectedFont
              ? `${fontLabel(selectedFont)} ${fontSupportsCharacter ? "supports" : "does not support"} this character`
              : "No font selected"}
          </dd>
        </div>
      </dl>
    </section>
  );
}

