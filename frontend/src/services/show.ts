import { Show } from '../models/show';
import apiRequest from '../routing/Request';

export class ShowService {
    async getUpcomingShows(): Promise<Show[]> {
        return await apiRequest('/api/shows/upcoming');
    }
}

export default new ShowService();
