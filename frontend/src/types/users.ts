export interface UserBaseSchema {
    name: string,
    email: string
}

export interface CreateUserSchema extends UserBaseSchema {
    password: string,
    password_confirm: string
}

export interface UserResponseSchema extends UserBaseSchema {
    id: string,
    role: string,
    balance: number,
    created_at: string
}