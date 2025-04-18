import { Show } from '../models/show';
import apiRequest from '../routing/Request';

/**
 * Service for managing show-related API requests.
 */
export class ShowService {
    /**
     * Fetches a list of upcoming shows from the API.
     *
     * @returns {Promise<Show[]>} A promise that resolves to an array of Show objects.
     */
    async getUpcomingShows(): Promise<Show[]> {
        return await apiRequest('/api/shows/upcoming');
    }
}

export default new ShowService();
