import React, { useEffect, useState } from 'react';
import ShowDetail from './ShowDetails';
import styles from './Shows.module.css';

interface Show {
    name: string;
    date: string;
    time: string;
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
                const response = await fetch('http://localhost:5000/api/shows');
                if (response.ok) {
                    const data = await response.json();
                    setShows(data);
                } else {
                    console.error('Failed to get shows:', response.statusText);
                }
            } catch (error) {
                console.error('Error getting shows:', error);
            }
        };

        getShows();
    }, []);

    const openShowDetail = (show: Show) => {
        setSelectedShow(show);
    };

    const closeShowDetail = () => {
        setSelectedShow(null);
    };

    return (
        <div className="container">
            <center>
                <h2>Where to catch us next</h2>
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
                                <span className={styles['show-time']}>
                                    {show.time}
                                </span>
                                <span className={styles['show-date']}>
                                    {show.date}
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
