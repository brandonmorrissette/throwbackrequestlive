import React, { useEffect, useState } from 'react';
import { useError } from '../../contexts/ErrorContext';
import { default as DataService } from '../../services/data';

import { Show } from '../../models/show';
import { default as ShowService } from '../../services/show';
import ShowDetail from './ShowDetails';
import styles from './Shows.module.css';

/**
 * Shows component that displays a list of shows and their details.
 * @component
 */
const Shows: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const { setError } = useError();

    useEffect(() => {
        const getShows = async () => {
            try {
                setShows(await ShowService.getUpcomingShows());
            } catch (error: any) {
                console.error('Error getting shows:', error);
                error.message = "We couldn't get the list of shows.";
                setError(error);
            }
        };

        getShows();
    }, [DataService]);

    const openShowDetail = (show: Show) => {
        setSelectedShow(show);
    };

    const closeShowDetail = () => {
        setSelectedShow(null);
    };

    return (
        <div className="container">
            <center>
                <h2>Come Jam With Us!</h2>
            </center>
            <div className="list-group">
                {shows.map((show, index) => (
                    <a
                        key={index}
                        href="#"
                        className={`list-group-item list-group-item-action ${styles['list-group-item']}`}
                        onClick={(e) => {
                            e.preventDefault();
                            openShowDetail(show);
                        }}
                    >
                        <div
                            className={`d-flex w-100 justify-content-between ${styles['show-title']}`}
                        >
                            <h5
                                className={`${styles['show-detail']} ${styles['show-name']}`}
                            >
                                {show.name}
                            </h5>
                            <h5
                                className={`${styles['show-detail']} ${styles['show-venue']}`}
                            >
                                {show.venue}
                            </h5>
                        </div>
                        <div
                            className={`d-flex justify-content-between ${styles['show-details']}`}
                        >
                            <div className={styles['show-start-time-parent']}>
                                <span
                                    className={`${styles['show-detail']} ${styles['show-start-time']}`}
                                >
                                    {show.start_time}
                                </span>
                            </div>
                            <span
                                className={`${styles['show-detail']} ${styles['show-address']}`}
                            >
                                {show.street && <div>{show.street}</div>}
                                <div>
                                    {show.city}, {show.state}
                                </div>
                            </span>
                        </div>
                    </a>
                ))}
            </div>

            {selectedShow && (
                <ShowDetail show={selectedShow} onClose={closeShowDetail} />
            )}
        </div>
    );
};

export default Shows;
