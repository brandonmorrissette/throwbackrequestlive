import React from 'react';
import { Show } from '../../models/show';
import styles from './Shows.module.css';

interface UpcomingShowsProps {
    shows: Show[];
    onShowSelect: (show: Show) => void;
}

/**
 * UpcomingShows component that displays a list of upcoming shows.
 * @component
 */
const UpcomingShows: React.FC<UpcomingShowsProps> = ({
    shows,
    onShowSelect,
}) => {
    return (
        <>
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
                            onShowSelect(show);
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
        </>
    );
};

export default UpcomingShows;
