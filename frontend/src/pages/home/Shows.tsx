import React, { useEffect, useState } from 'react';
import { default as DataService } from '../../services/data';
import ShowDetail from './ShowDetails';
import styles from './Shows.module.css';

export interface Show {
    name: string;
    datetime: string;
    venue: string;
    street: string;
    city: string;
    state: string;
}

const Shows: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);

    useEffect(() => {
        const getShows = async () => {
            try {
                const data = await DataService.readRows('shows');
                setShows(data);
            } catch (error) {
                console.error('Error getting shows:', error);
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
                <h2>Come See Us Play</h2>
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
                            <h5 className={styles['show-name']}>{show.name}</h5>
                            <h5 className={styles['show-venue']}>
                                {show.venue}
                            </h5>
                        </div>
                        <div
                            className={`d-flex justify-content-between ${styles['show-details']}`}
                        >
                            <div className={styles['show-date-time']}>
                                <span className={styles['show-datetime']}>
                                    {show.datetime}
                                </span>
                            </div>
                            <span className={styles['show-address']}>
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
