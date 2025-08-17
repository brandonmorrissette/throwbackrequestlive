import React, { useEffect, useState } from 'react';
import { useError } from '../../contexts/ErrorContext';
import { default as DataService } from '../../services/data';

import BookingForm from '../../components/form/BookingForm';
import { Show } from '../../models/show';
import { default as ShowService } from '../../services/show';
import ShowDetail from './ShowDetails';
import styles from './Shows.module.css';
import UpcomingShows from './UpcomingShows';

/**
 * Shows component that displays a list of shows and their details.
 * @component
 */
const Shows: React.FC = () => {
    const [upcomingShows, setUpcomingShows] = useState<Show[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const { setError } = useError();

    useEffect(() => {
        const getUpcomingShows = async () => {
            try {
                setUpcomingShows(await ShowService.getUpcomingShows());
            } catch (error: any) {
                console.error('Error getting shows:', error);
                error.message = "We couldn't get the list of shows.";
                setError(error);
            }
        };

        getUpcomingShows();
    }, [DataService]);

    const openShowDetail = (show: Show) => {
        setSelectedShow(show);
    };

    const closeShowDetail = () => {
        setSelectedShow(null);
    };

    return (
        <div className="container">
            {upcomingShows.length > 0 ? (
                <>
                    <UpcomingShows
                        shows={upcomingShows}
                        onShowSelect={openShowDetail}
                    />

                    {selectedShow && (
                        <ShowDetail
                            show={selectedShow}
                            onClose={closeShowDetail}
                        />
                    )}
                </>
            ) : (
                <>
                    <h2 className={styles.noShowsMessage}>
                        Sorry! We don't have any shows currently scheduled.
                    </h2>
                    <hr />
                    <BookingForm />
                </>
            )}
        </div>
    );
};

export default Shows;
