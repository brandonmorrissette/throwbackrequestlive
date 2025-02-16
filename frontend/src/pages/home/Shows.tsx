import React, { useEffect, useState } from 'react';
import { useError } from '../../contexts/ErrorContext';
import { default as DataService } from '../../services/data';
import ShowDetail from './ShowDetails';
import styles from './Shows.module.css';

export class Show {
    name: string;
    datetime: string;
    venue: string;
    street: string;
    city: string;
    state: string;

    constructor(show: Show) {
        this.name = show.name;
        this.datetime = this.formatDateTime(show.datetime);
        this.venue = show.venue;
        this.street = show.street;
        this.city = show.city;
        this.state = show.state;
    }

    private formatDateTime(datetime: string): string {
        const date = new Date(datetime);
        const formattedDate = date.toLocaleDateString('en-US', {
            weekday: 'short',
            month: 'short',
            day: '2-digit',
            year: 'numeric',
        });
        const formattedTime = date.toLocaleTimeString('en-US', {
            hour: 'numeric',
            minute: '2-digit',
            hour12: true,
        });
        return `${formattedDate} ${formattedTime}`;
    }
}

const Shows: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const { setError } = useError();

    useEffect(() => {
        const getShows = async () => {
            try {
                const now = new Date();
                const startOfDay = `${
                    now.toISOString().split('T')[0]
                } 00:00:00`;

                console.log('startOfDay:', startOfDay);
                const filters = [`datetime >= ${startOfDay}`];
                const data = await DataService.readRows('shows', {
                    filters: filters,
                });
                setShows(data.map((show: any) => new Show(show)));
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
