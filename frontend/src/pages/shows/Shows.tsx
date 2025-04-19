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
                        className={`list-group-item list-group-item-action`}
                        onClick={(e) => {
                            e.preventDefault();
                            openShowDetail(show);
                        }}
                    >
                        <div
                            className={`d-flex w-100 justify-content-center ${styles.showTitle}`}
                        >
                            <h5
                                className={`${styles.showDetail} ${styles.showName}`}
                            >
                                {show.name}
                            </h5>
                            <h5
                                className={`${styles.showDetail} ${styles.showVenue}`}
                            >
                                {show.venue}
                            </h5>
                        </div>
                        <div
                            className={`d-flex w-100 justify-content-center ${styles.showDetails}`}
                        >
                            <span
                                className={`${styles.showDetail} ${styles.showStartTime}`}
                            >
                                {show.start_time}
                            </span>
                            <span
                                className={`${styles.showDetail} ${styles.showAddress}`}
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
