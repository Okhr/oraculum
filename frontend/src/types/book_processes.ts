
export interface BookProcessResponseSchema {
    book_id: string,
    is_requested: boolean
    estimated_cost: number
    requested_at?: string
    completeness?: number
}