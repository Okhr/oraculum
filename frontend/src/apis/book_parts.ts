import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { BookPartResponseSchema, BookPartUpdateSchema } from '../types/book_parts';


export const useGetBookPart = () => {
    const authHeader = useAuthHeader();

    const getBookPart = async (bookPartId: string): Promise<BookPartResponseSchema> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<BookPartResponseSchema>(globalConfig.API_URL + `/book_parts/book_part_id/${bookPartId}`, config);
        return response.data;
    };

    return { getBookPart };
};

export const useGetBookParts = () => {
    const authHeader = useAuthHeader();

    const getBookParts = async (bookId: string): Promise<BookPartResponseSchema[]> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<BookPartResponseSchema[]>(globalConfig.API_URL + `/book_parts/book_id/${bookId}`, config);
        return response.data;
    };

    return { getBookParts };
};


export const useUpdateBookPart = () => {
    const authHeader = useAuthHeader();

    const updateBookPart = async (bookPartId: string, bookPartUpdate: BookPartUpdateSchema): Promise<BookPartUpdateSchema> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };
        
        const response = await axios.put<BookPartUpdateSchema>(globalConfig.API_URL + `/book_parts/update/${bookPartId}`, bookPartUpdate, config);
        return response.data;
    };

    return { updateBookPart };
};