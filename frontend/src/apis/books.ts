import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { BookResponseSchema, BookUploadResponseSchema } from '../types/books';

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

export const useGetUploadedBooks = () => {
    const authHeader = useAuthHeader();

    const getUploadedBooks = async (): Promise<BookResponseSchema[]> => {
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

    return { getUploadedBooks };
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