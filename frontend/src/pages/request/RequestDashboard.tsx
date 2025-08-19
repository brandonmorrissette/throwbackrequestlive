import 'chart.js/auto';
import React, { useEffect, useRef, useState } from 'react';
import { BarDashboard } from '../../components/dashboard/Dashboard';
import { useAuth } from '../../contexts/AuthContext';
import { Show } from '../../models/show';
import { Song } from '../../models/song';
import { default as RequestService } from '../../services/request';
import { default as ShowService } from '../../services/show';
import './RequestDashboard.css';

/**
 * RequestDashboard Component
 *
 * This component displays a dashboard for managing and visualizing song requests for different shows.
 * It allows users to:
 * - Select a show from a dropdown menu.
 * - View a bar chart of song request counts for the selected show.
 * - Sync the data to ensure it is up-to-date.
 *
 * Dependencies:
 * - Uses the `BarDashboard` class to encapsulate the chart rendering and sync button logic.
 * - Fetches data from the backend using `RequestService`.
 */
const RequestDashboard: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [songs, setSongs] = useState<Song[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const [songRequestCounts, setSongRequestCounts] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const { token } = useAuth();
    const [, setSyncing] = useState<boolean>(false);
    const chartRef = useRef<any>(null);

    /**
     * Fetches the list of shows and songs from the backend.
     * Populates the `shows` and `songs` state variables.
     */
    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const shows = await ShowService.getShows();
                const songs = await RequestService.getRows('songs', token);
                setShows(shows.map((show: any) => new Show(show)));
                setSongs(songs);
            } catch (error) {
                console.error('Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };
        fetchData();
    }, []);

    /**
     * Handles the selection of a show from the dropdown.
     * Fetches the song request counts for the selected show.
     *
     * @param show - The selected show object.
     */
    const handleShowChange = async (show: Show) => {
        setSelectedShow(show);
        setLoading(true);
        try {
            const data = await RequestService.getCountOfRequestsByShowId(
                show.hash || ''
            );
            setSongRequestCounts(data);
        } catch (error) {
            console.error('Error fetching song request counts:', error);
        } finally {
            setLoading(false);
        }
    };

    /**
     * Syncs the song request counts for the currently selected show.
     * Updates the chart data and ensures the chart is refreshed.
     */
    const handleSync = async () => {
        if (!selectedShow) return;
        setSyncing(true);
        try {
            const data = await RequestService.getCountOfRequestsByShowId(
                selectedShow.hash || ''
            );
            setSongRequestCounts(data);
            if (chartRef.current) {
                chartRef.current.chartInstance.update();
            }
        } catch (error) {
            console.error('Error syncing data:', error);
        } finally {
            setSyncing(false);
        }
    };

    const data = {
        labels: songRequestCounts.map((item: any) => {
            const song = songs.find((s: any) => s.id === item.song_id);
            return song ? [song.band_name, song.song_name] : 'Unknown';
        }),
        datasets: [
            {
                data: songRequestCounts.map((item: any) => item.count),
            },
        ],
    };

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
                            {`${show.venue} - ${new Date(
                                show.start_time
                            ).toLocaleString()}`}
                        </option>
                    ))}
                </select>
            </div>

            {selectedShow && songRequestCounts.length > 0 && (
                <BarDashboard
                    chartRef={chartRef}
                    data={data}
                    syncFunction={handleSync}
                />
            )}
        </div>
    );
};

export default RequestDashboard;
