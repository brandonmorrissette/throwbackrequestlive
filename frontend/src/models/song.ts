export class Song {
    display_name: string;
    band_name: string;
    song_name: string;

    /**
     * Create a Song
     * @param {Song} song - The song data.
     */
    constructor(song: Song) {
        this.band_name = song.band_name;
        this.song_name = song.song_name;
        this.display_name = song.band_name + ' - ' + song.song_name;
    }
}
