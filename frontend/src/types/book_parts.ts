export interface LightBookPartResponseSchema {
    id: string;
    book_id: string;
    parent_id: string | null;
    label: string;
    sibling_index: number;
    is_story_part: boolean;
    is_entity_extracted: boolean;
    created_at: Date;
    level: number;
}

export interface BookPartResponseSchema extends LightBookPartResponseSchema {
    content: string;
}

export interface BookPartUpdateSchema {
    is_story_part: boolean;
}
