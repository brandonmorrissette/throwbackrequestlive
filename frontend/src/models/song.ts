export class Song {
    id: string;
    band_name: string;
    song_name: string;

    /**
     * Create a Song
     * @param {Song} song - The song data.
     */
    constructor(song: Song) {
        this.id = song.id;
        this.band_name = song.band_name;
        this.song_name = song.song_name;
    }
}
