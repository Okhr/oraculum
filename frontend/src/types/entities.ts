export type CategoryType = 'PERSON' | 'LOCATION' | 'ORGANIZATION' | 'CONCEPT';

export interface Fact {
  book_part_id: string;
  content: string;
  sibling_index: number;
  sibling_total: number;
}

export interface EntityResponseSchema {
  name: string;
  alternative_names: string[];
  category: string;
  facts: Fact[];
}
