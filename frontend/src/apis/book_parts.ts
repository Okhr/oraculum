import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { TocBookPartResponseSchema } from '../types/book_parts';

export const useGetTableOfContent = () => {
    const authHeader = useAuthHeader();

    const getTableOfContent = async (bookId: string): Promise<TocBookPartResponseSchema[]> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<TocBookPartResponseSchema[]>(globalConfig.API_URL + `/bookparts/toc/${bookId}`, config);
        return response.data;
    };

    return { getTableOfContent };
};
