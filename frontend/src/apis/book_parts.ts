import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { TocBookPartResponseSchema, BookPartResponseSchema } from '../types/book_parts';

export const useGetTableOfContent = () => {
    const authHeader = useAuthHeader();

    const getTableOfContent = async (bookId: string): Promise<TocBookPartResponseSchema[]> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<TocBookPartResponseSchema[]>(globalConfig.API_URL + `/book_parts/toc/${bookId}`, config);
        return response.data;
    };

    return { getTableOfContent };
};

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
