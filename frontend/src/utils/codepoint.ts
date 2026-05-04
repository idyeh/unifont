export function charFromCodepoint(codepoint: number): string {
  return String.fromCodePoint(codepoint);
}

export function formatCodepoint(codepoint: number): string {
  return `U+${codepoint.toString(16).toUpperCase().padStart(4, "0")}`;
}

export function fontLabel(font: { family_name: string | null; full_name: string | null }): string {
  return font.family_name || font.full_name || "Unnamed font";
}
