import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import Modal from '../../components/modal/Modal';
import { useError } from '../../contexts/ErrorContext';
import {
    DuplicateRequestError,
    default as RequestService,
} from '../../services/request';
import styles from './Request.module.css';

interface Song {
    song_name: string;
    band_name: string;
    id: string;
}

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

    useEffect(() => {
        const enforcer = async () => {
            try {
                await RequestService.enforceUniqueRequest(showId);
            } catch (error: any) {
                setError(error);
                if (error instanceof DuplicateRequestError) {
                    console.warn('Duplicate request:', error.message);
                    navigate('/?song=' + encodeURIComponent(error.song_name));
                }
            }
        };
        enforcer();
    }, [navigate]);

    useEffect(() => {
        if (!showId) {
            const error = new Error('Show ID is missing in the request');
            console.error(error);
            setError(error);
            navigate('/');
        }
    }, [showId]);

    useEffect(() => {
        const songs = RequestService.readRows('songs');
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
            RequestService.writeRequest(selectedSong.id, showId);
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
                        <button
                            type="button"
                            className="btn btn-custom"
                            onClick={handleRequest}
                        >
                            Confirm
                        </button>
                    </div>
                </Modal>
            )}
        </div>
    );
};

export default Request;
