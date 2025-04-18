import { Song } from '../models/song';
import apiRequest from '../routing/Request';
import { DataService } from './data';

/**
 * Service for handling requests related to songs and shows.
 */
export class RequestService extends DataService {
    /**
     * Retrieves the count of requests for a specific show by its ID.
     * @param showId - The ID of the show.
     * @returns A promise resolving to an array containing the count of requests.
     */
    async getCountOfRequestsByShowId(showId: string): Promise<any[]> {
        return await apiRequest(`/api/requests/count?showId=${showId}`);
    }

    /**
     * Submits a new request for a song in a specific show.
     * @param song - The song object containing song details.
     * @param showId - The ID of the show.
     * @returns A promise resolving to the response of the request submission.
     */
    async putRequest(song: Song, showId: string): Promise<any[]> {
        return await apiRequest(`/api/requests`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                song_id: song.id,
                show_id: showId,
            }),
        });
    }
}

export default new RequestService();
