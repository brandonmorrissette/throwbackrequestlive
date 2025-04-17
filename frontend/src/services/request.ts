import { Song } from '../models/song';
import apiRequest from '../routing/Request';
import { DataService } from './data';

export class RequestService extends DataService {
    async getCountOfRequestsByShowId(showId: string): Promise<any[]> {
        return await apiRequest(`/api/requests/count?showId=${showId}`);
    }

    async recordRequest(song: Song, showId: string): Promise<any[]> {
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
