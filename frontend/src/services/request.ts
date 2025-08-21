import { Song } from '../models/song';
import apiRequest from '../routing/Request';
import { DataService } from './data';

/**
 * Service for handling requests related to songs and shows.
 */
export class RequestService extends DataService {
    /**
     * Retrieves the count of requests for a specific show by its ID.
     * @param showHash - The ID of the show.
     * @returns A promise resolving to an array containing the count of requests.
     */
    async getTop10RequestsByShowHash(showHash: string): Promise<any[]> {
        const data = await apiRequest(`/api/requests/counts/${showHash}`);

        return Object.entries(data)
            .map(([display_name, count]) => ({ display_name, count }))
            .sort((a: any, b: any) => b.count - a.count)
            .slice(0, 10);
    }

    /**
     * Submits a new request for a song in a specific show.
     * @param song - The song object containing song details.
     * @param showHash - The ID of the show.
     * @returns A promise resolving to the response of the request submission.
     */
    async postRequest(song: Song, showHash: string): Promise<any[]> {
        let url = `/api/requests`;
        if (showHash == 'DEMO') {
            url += `/DEMO`;
        }

        return await apiRequest(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                display_name: song.display_name,
                show_hash: showHash,
            }),
        });
    }
}

export default new RequestService();
