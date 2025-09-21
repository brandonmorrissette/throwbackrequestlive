import { Song } from '../models/song';
import apiRequest from '../routing/Request';

/**
 * Service for managing song-related API requests.
 */
export class SongService {
    /**
     * Fetches a list of songs from the API.
     *
     * @param {string | null} token - The authentication token.
     * @returns {Promise<Song[]>} A promise that resolves to an array of Song objects.
     */
    async getSongs(): Promise<Song[]> {
        const response = await apiRequest('/api/songs');
        console.log(response);
        return response.map((songData: any) => new Song(songData));
    }
}

export default new SongService();
