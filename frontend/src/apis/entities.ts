import axios from 'axios';
import useAuthHeader from 'react-auth-kit/hooks/useAuthHeader';
import globalConfig from "../config.json";
import { EntityResponseSchema } from '../types/entities';

export const useGetBookEntities = () => {
    const authHeader = useAuthHeader();

    const getBookEntities = async (bookId: string): Promise<EntityResponseSchema[]> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<EntityResponseSchema[]>(globalConfig.API_URL + `/entities/book_id/${bookId}`, config);
        return response.data;
    };

    return { getBookEntities };
};
