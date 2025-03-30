import { DataService } from './data';

class RequestService extends DataService {
    async writeRequest(song_id: string, show_id: string): Promise<void> {
        const body = {
            song_id: song_id,
            request_time: new Date(),
            show_id: show_id,
            request_id: getDeviceInfo(),
        };
        this.writeRows('requests', [body]);
    }
}

const getDeviceInfo = (): string => {
    if (navigator.userAgent) {
        console.log('User agent:', navigator.userAgent);
        return navigator.userAgent;
    }

    throw new Error(
        'User agent is not available. Unable to produce unique request id.'
    );
};

export default new RequestService();
