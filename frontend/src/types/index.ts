export type UnicodeBlock = {
  id: number;
  name: string;
  start_codepoint: number;
  end_codepoint: number;
  plane: string;
  sort_order: number;
};

export type UnicodeCharacter = {
  id?: number;
  codepoint: number;
  display_codepoint: string;
  char: string;
  name: string;
  block_id?: number;
  block_name?: string;
  category: string;
  script?: string | null;
  plane: string;
};

export type PaginatedCharacters = {
  items: UnicodeCharacter[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};

export type FontSummary = {
  id: number;
  family_name: string | null;
  full_name: string | null;
  postscript_name: string | null;
  style: string | null;
  file_format: string;
  file_size: number;
  supported_codepoint_count: number;
  created_at: string;
};

export type CoverageCharacter = {
  codepoint: number;
  display_codepoint: string;
  char: string;
  name: string;
};

export type BlockCoverage = {
  font_id: number;
  block_id: number;
  block_name: string;
  total_codepoints: number;
  supported_count: number;
  missing_count: number;
  coverage_percentage: number;
  supported_characters: CoverageCharacter[];
  missing_characters: CoverageCharacter[];
  list_limit: number;
};

export type FontCharacterSupport = {
  font_id: number;
  codepoint: number;
  display_codepoint: string;
  supported: boolean;
};

export type FontCoveragePageCharacter = UnicodeCharacter & {
  supported: boolean;
};

export type FontCoveragePage = {
  items: FontCoveragePageCharacter[];
  page: number;
  page_size: number;
  total: number;
  total_pages: number;
};
