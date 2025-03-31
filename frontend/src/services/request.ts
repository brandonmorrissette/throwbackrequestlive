import { DataService } from './data';

export class DuplicateRequestError extends Error {
    song_name: string;

    constructor(message: string, song_name: string) {
        super(message);
        this.name = 'DuplicateRequestError';
        this.song_name = song_name;
    }
}

class RequestService extends DataService {
    async enforceUniqueRequest(showId: string) {
        const requestId = localStorage.getItem('requestId');
        console.log('Request ID:', requestId);

        if (requestId) {
            const requestResponse = await this.readRows('requests', {
                filters: ['request_id = ' + requestId, 'show_id = ' + showId],
            });
            console.log('Request', requestResponse);
            if (!requestResponse.length) return;

            const songId = requestResponse[0].song_id;
            const songResponse = await this.readRows('songs', {
                filters: ['id = ' + songId],
            });
            console.log('Song', songResponse);
            const songName = songResponse[0].song_name;

            throw new DuplicateRequestError(
                `Requester ` + requestId + ' already requested ' + songName,
                songName
            );
        }
    }

    async writeRequest(song_id: string, show_id: string): Promise<void> {
        const requestId = localStorage.getItem('requestId');
        if (requestId) return;

        const hash =
            show_id + (await hashNavigatorInfo()) + crypto.randomUUID();
        console.log('Request ID:', hash);
        localStorage.setItem('requestId', hash);

        this.writeRows('requests', [
            {
                song_id: song_id,
                request_time: new Date(),
                show_id: show_id,
                request_id: hash,
            },
        ]);
    }
}

const hashNavigatorInfo = async (): Promise<string> => {
    const navigatorData: Record<string, any> = {};

    for (const key in navigator) {
        if (typeof navigator[key as keyof Navigator] !== 'function') {
            console.log(key, navigator[key as keyof Navigator]);
            navigatorData[key] = navigator[key as keyof Navigator];
        }
    }

    const navigatorString = JSON.stringify(navigatorData);

    const encoder = new TextEncoder();
    const data = encoder.encode(navigatorString);
    const hashBuffer = await crypto.subtle.digest('SHA-256', data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));

    return hashArray.map((byte) => byte.toString(16).padStart(2, '0')).join('');
};

export default new RequestService();
