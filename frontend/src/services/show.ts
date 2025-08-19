import { Show } from '../models/show';
import apiRequest, { createBearerHeader } from '../routing/Request';

/**
 * Service for managing show-related API requests.
 */
export class ShowService {
    /**
     * Fetches a list of shows from the API.
     *
     * @param {string | null} token - The authentication token.
     * @returns {Promise<Show[]>} A promise that resolves to an array of Show objects.
     */
    async getShows(): Promise<Show[]> {
        const response = await apiRequest('/api/shows');
        return response.map((showData: any) => new Show(showData));
    }

    /**
     * Fetches a list of upcoming shows from the API.
     *
     * @returns {Promise<Show[]>} A promise that resolves to an array of Show objects.
     */
    async getUpcomingShows(): Promise<Show[]> {
        const response = await apiRequest('/api/shows/upcoming');
        return response.map((showData: any) => new Show(showData));
    }

    /**
     * Inserts a new show into the API.
     *
     * @param {any} show - The show data to insert.
     * @returns {Promise<void>} A promise that resolves when the show is inserted.
     */
    async insertShow(show: any, token: string | null): Promise<void> {
        await apiRequest('/api/shows', {
            method: 'POST',
            headers: {
                ...createBearerHeader(token).headers,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(show),
        });
    }
}

export default new ShowService();
