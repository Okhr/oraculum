export interface BookBaseSchema {
    user_id: string,
    author: string,
    title: string
}

export interface BookUploadResponseSchema extends BookBaseSchema {
    id: string,
    upload_date: string,
    file_type: string,
    original_file_name: string,
    file_size: number
}

export interface BookResponseSchema extends BookBaseSchema {
    id: string,
    upload_date: string,
    file_type: string
}