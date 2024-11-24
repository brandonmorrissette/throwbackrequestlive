import React, { useEffect, useState } from 'react';
import Modal from '../../app/modal/Modal'; // Import your custom modal
import styles from './Vote.module.css';

interface Song {
    song_name: string;
    band: string;
}

const Vote: React.FC = () => {
    const [songs, setSongs] = useState<Song[]>([]);
    const [selectedSong, setSelectedSong] = useState<string | null>(null);

    useEffect(() => {
        fetch('/api/songs')
            .then((response) => response.json())
            .then((data) => setSongs(data));
    }, []);

    const handleVote = () => {
        if (selectedSong) {
            fetch('/api/vote', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ song: selectedSong }),
            }).then((response) => {
                if (response.redirected) {
                    window.location.href = response.url;
                }
            });
        }
    };

    return (
        <div>
            <h2>Vote Now!</h2>
            <div className="list-group">
                {songs.map((song, index) => (
                    <button
                        key={index}
                        type="button"
                        className={styles.voteButton}
                        onClick={() => setSelectedSong(song.song_name)}
                    >
                        <div className={styles.songDetails}>
                            <span className={styles.songBand}>{song.band}</span>
                            <span className={styles.songName}>
                                {song.song_name}
                            </span>
                        </div>
                    </button>
                ))}
            </div>

            {selectedSong && (
                <Modal onClose={() => setSelectedSong(null)}>
                    {' '}
                    {/* Use the custom modal */}
                    <h3>Confirm Your Selection</h3>
                    <p>Are you sure you want to select:</p>
                    <p>
                        <strong>{selectedSong}</strong>
                    </p>
                    <div className={styles.modalActions}>
                        <button
                            type="button"
                            className="btn btn-custom"
                            onClick={handleVote}
                        >
                            Confirm
                        </button>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default Vote;
