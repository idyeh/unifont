import type { UnicodeBlock } from "../types";
import { formatCodepoint } from "../utils/codepoint";

type Props = {
  blocks: UnicodeBlock[];
  selectedBlockId?: number;
  onSelect: (block: UnicodeBlock) => void;
};

export function BlockNavigator({ blocks, selectedBlockId, onSelect }: Props) {
  return (
    <aside className="block-nav" aria-label="Unicode blocks">
      <div className="panel-title">Blocks</div>
      <div className="block-list">
        {blocks.map((block) => (
          <button
            key={block.id}
            className={block.id === selectedBlockId ? "block-item active" : "block-item"}
            onClick={() => onSelect(block)}
          >
            <span>{block.name}</span>
            <small>
              {formatCodepoint(block.start_codepoint)}-{formatCodepoint(block.end_codepoint)}
            </small>
          </button>
        ))}
      </div>
    </aside>
  );
}

