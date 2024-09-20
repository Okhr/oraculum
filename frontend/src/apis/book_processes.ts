import axios from "axios";
import useAuthHeader from "react-auth-kit/hooks/useAuthHeader";
import globalConfig from "../config.json";
import { BookProcessResponseSchema } from '../types/book_processes';

export const useTriggerExtraction = () => {
    const authHeader = useAuthHeader();

    const triggerExtraction = async (bookId: string): Promise<void> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        await axios.post(globalConfig.API_URL + `/processes/trigger_extraction/${bookId}`, {}, config);
    };

    return { triggerExtraction };
};

export const useGetEntityExtractionProcess = () => {
    const authHeader = useAuthHeader();

    const getEntityExtractionProcess = async (bookId: string): Promise<BookProcessResponseSchema> => {
        const config = {
            headers: {
                'Authorization': authHeader,
            },
        };

        const response = await axios.get<BookProcessResponseSchema>(globalConfig.API_URL + `/processes/entity_extraction/${bookId}`, config);
        return response.data;
    };

    return { getEntityExtractionProcess };
};
