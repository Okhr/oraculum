export interface BookPartBaseSchema {
    id: string;
    book_id: string;
    parent_id: string | null;
    label: string;
    created_at: Date;
}

export interface TocBookPartResponseSchema extends BookPartBaseSchema {
    sibling_index: number;
    is_story_part: boolean;
    children: TocBookPartResponseSchema[] | null;
}

export interface BookPartResponseSchema extends BookPartBaseSchema {
    content: string;
    sibling_index: number;
    is_story_part: boolean;
    is_entity_extracted: boolean;
    created_at: Date;
}

export interface BookPartUpdateSchema {
    is_story_part: boolean;
}
