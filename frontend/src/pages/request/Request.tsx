import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Modal from '../../components/modal/Modal';
import { useAuth } from '../../contexts/AuthContext';
import { useError } from '../../contexts/ErrorContext';
import { Song } from '../../models/song';
import { default as AuthService } from '../../services/auth';
import { default as RequestService } from '../../services/request';
import styles from './Request.module.css';

/**
 * Request component allows users to select and request a song.
 *
 * @component
 * @example
 * return (
 *   <Request />
 * )
 */
const Request: React.FC = () => {
    const [songs, setSongs] = useState<Song[]>([]);
    const [selectedSong, setSelectedSong] = useState<Song | null>(null);

    const [searchParams] = useSearchParams();
    const showId = searchParams.get('showId') || '';

    const navigate = useNavigate();
    const { setError } = useError();
    const { token } = useAuth();

    useEffect(() => {
        const validate = async () => {
            try {
                const response = await AuthService.validateSession();

                if (!response.success) {
                    throw new Error('Session validation failed');
                }
            } catch (error: any) {
                console.error('Error validating session:', error);
                setError(error);
                navigate('/');
            }
        };

        validate();
    }, [navigate, setError]);

    useEffect(() => {
        const songs = RequestService.getRows('songs', token);
        songs
            .then((data) => {
                setSongs(data);
            })
            .catch((error) => {
                error.message = 'Error fetching songs: ' + error.message;
                console.error(error);
                setError(error);
            });
    }, []);

    const handleRequest = async () => {
        if (selectedSong) {
            RequestService.putRequest(selectedSong, showId);
            navigate(
                '/?songName=' + encodeURIComponent(selectedSong.song_name)
            );
        }
    };

    return (
        <div>
            <h2>Request Now!</h2>
            <div className="list-group">
                {songs.map((song, index) => (
                    <button
                        key={index}
                        type="button"
                        className={styles.requestButton}
                        onClick={() => setSelectedSong(song)}
                    >
                        <div className={styles.songDetails}>
                            <span className={styles.songBand}>
                                {song.band_name}
                            </span>
                            <span className={styles.songName}>
                                {song.song_name}
                            </span>
                        </div>
                    </button>
                ))}
            </div>

            {selectedSong && (
                <Modal onClose={() => setSelectedSong(null)}>
                    <h3>Confirm Your Selection</h3>
                    <p>Are you sure you want to select:</p>
                    <p>
                        <strong>{selectedSong.song_name}</strong>
                    </p>
                    <div className={styles.modalActions}>
                        <button type="button" onClick={handleRequest}>
                            Confirm
                        </button>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default Request;
