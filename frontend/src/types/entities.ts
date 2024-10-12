export type CategoryType = 'PERSON' | 'LOCATION' | 'ORGANIZATION' | 'CONCEPT';

export interface Fact {
  book_part_id: string;
  content: string;
  occurrences: number;
  sibling_index: number | null;
  sibling_total: number | null;
}

export interface EntityResponseSchema {
  name: string;
  alternative_names: string[];
  category: string;
  facts: Fact[];
}
