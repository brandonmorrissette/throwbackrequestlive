import React, { useEffect, useState } from 'react';
import { Show } from '../../models/show';
import { default as RequestService } from '../../services/request';
import { default as ShowService } from '../../services/show';
import './RequestDashboard.css';

const RequestDashboard: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const [songRequestCounts, setSongRequestCounts] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [, setSyncing] = useState<boolean>(false);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const shows = await ShowService.getShows();
                setShows(shows.map((show: any) => new Show(show)));
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    const handleShowChange = (show: Show) => {
        console.log('Selected show:', show);
        setSelectedShow(show);
    };

    const handleSync = async (show: Show | null = selectedShow) => {
        if (!show) return;
        console.log('Syncing data for show:', show);
        setSyncing(true);
        try {
            const data = await RequestService.getTop10RequestsByShowHash(
                show.hash || ''
            );
            setSongRequestCounts(data);
        } catch (error) {
            console.error('Error syncing data:', error);
        } finally {
            setSyncing(false);
        }
    };

    useEffect(() => {
        handleSync(selectedShow);
    }, [selectedShow]);

    const maxCount =
        songRequestCounts.length > 0
            ? Math.max(...songRequestCounts.map((item) => item.count))
            : 1;

    return (
        <div>
            <h1>Request Dashboard</h1>
            {loading && <p>Loading...</p>}

            <div>
                <label htmlFor="showSelect">Select a Show: </label>
                <select
                    id="showSelect"
                    onChange={(e) => {
                        const selectedShow = shows.find(
                            (show) => show.hash === e.target.value
                        );
                        if (selectedShow) {
                            handleShowChange(selectedShow);
                        }
                    }}
                    disabled={loading}
                >
                    <option value="">-- Select a Show --</option>
                    {shows.map((show) => (
                        <option key={show.hash} value={show.hash}>
                            {`${show.name} - ${show.venue} - ${new Date(
                                show.start_time
                            ).toLocaleString()}`}
                        </option>
                    ))}
                </select>
            </div>

            {selectedShow && songRequestCounts.length > 0 && (
                <div className="request-table">
                    <button onClick={() => handleSync(selectedShow)}>
                        Sync
                    </button>
                    <table>
                        <thead>
                            <tr>
                                <th>Song</th>
                                <th>Count</th>
                            </tr>
                        </thead>
                        <tbody>
                            {songRequestCounts.map((item, index) => (
                                <tr key={index}>
                                    <td>
                                        <b>{item.display_name}</b>
                                    </td>
                                    <td className="count-cell">
                                        <div className="count-container">
                                            <span className="count">
                                                {item.count}
                                            </span>
                                            <div className="bar-container">
                                                <div
                                                    className="bar"
                                                    style={{
                                                        width: `${
                                                            (item.count /
                                                                maxCount) *
                                                            100
                                                        }%`,
                                                    }}
                                                />
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
};

export default RequestDashboard;
