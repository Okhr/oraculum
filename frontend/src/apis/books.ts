import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { BookResponseSchema, BookUploadResponseSchema, BookUpdateSchema } from '../types/books';

export const useUploadBook = () => {
    const authHeader = useAuthHeader();

    const uploadBook = async (file: File): Promise<BookUploadResponseSchema> => {
        const formData = new FormData();
        formData.append('uploaded_file', file);

        const config = {
            headers: {
                'content-type': 'multipart/form-data',
                'Authorization': authHeader,
            },
        };

        try {
            const response = await axios.post<BookUploadResponseSchema>(globalConfig.API_URL + '/books/upload/', formData, config);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    return { uploadBook };
};

export const useGetUserBooks = () => {
    const authHeader = useAuthHeader();

    const getUserBooks = async (): Promise<BookResponseSchema[]> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };
        try {
            const response = await axios.get<BookResponseSchema[]>(globalConfig.API_URL + '/books/', config);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    return { getUserBooks };
};

export const useDeleteBook = () => {
    const authHeader = useAuthHeader();

    const deleteBook = async (bookId: string): Promise<BookResponseSchema> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };
        try {
            const response = await axios.delete<BookResponseSchema>(globalConfig.API_URL + `/books/delete/${bookId}`, config);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    return { deleteBook };
};

export const useUpdateBook = () => {
    const authHeader = useAuthHeader();

    const updateBook = async (bookId: string, updatedBook: BookUpdateSchema): Promise<BookResponseSchema> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };
        try {
            const response = await axios.put<BookResponseSchema>(globalConfig.API_URL + `/books/update/${bookId}`, updatedBook, config);
            return response.data;
        } catch (error) {
            throw error;
        }
    };

    return { updateBook };
};