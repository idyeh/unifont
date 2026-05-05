import type {
  BlockCoverage,
  FontCharacterSupport,
  FontCoveragePage,
  FontSummary,
  PaginatedCharacters,
  UnicodeBlock,
  UnicodeCharacter
} from "../types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, options);
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail ?? "Request failed");
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  blocks: () => request<UnicodeBlock[]>("/api/unicode/blocks"),
  characters: (blockId: number, page: number, pageSize = 128) =>
    request<PaginatedCharacters>(
      `/api/unicode/blocks/${blockId}/characters?page=${page}&page_size=${pageSize}`
    ),
  character: (codepoint: string) => request<UnicodeCharacter>(`/api/unicode/characters/${codepoint}`),
  fonts: () => request<FontSummary[]>("/api/fonts"),
  uploadFont: (file: File) => {
    const form = new FormData();
    form.append("file", file);
    return request<FontSummary>("/api/fonts/upload", {
      method: "POST",
      body: form
    });
  },
  coverage: (fontId: number, blockId: number) =>
    request<BlockCoverage>(`/api/fonts/${fontId}/coverage/${blockId}`),
  coveragePage: (fontId: number, blockId: number, page: number, pageSize = 128) =>
    request<FontCoveragePage>(
      `/api/fonts/${fontId}/coverage/${blockId}/characters?page=${page}&page_size=${pageSize}`
    ),
  characterSupport: (fontId: number, codepoint: string) =>
    request<FontCharacterSupport>(`/api/fonts/${fontId}/characters/${codepoint}/support`),
  fontFileUrl: (fontId: number) => `${API_BASE}/api/fonts/${fontId}/file`,
  saveFontConfig: (blockId: number, fontIds: number[]) =>
    request(`/api/font-config/${blockId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ font_ids: fontIds })
    })
};
