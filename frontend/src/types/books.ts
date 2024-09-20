export interface BookBaseSchema {
    user_id: string,
    author: string,
    title: string
}

export interface BookUploadResponseSchema extends BookBaseSchema {
    id: string,
    created_at: string,
    file_type: string,
    original_file_name: string,
    file_size: number,
    is_parsed: boolean
}

export interface BookResponseSchema extends BookBaseSchema {
    id: string,
    created_at: string,
    file_type: string,
    cover_image_base64?: string,
    is_parsed: boolean
}

export interface BookUpdateSchema {
    author?: string,
    title?: string
}