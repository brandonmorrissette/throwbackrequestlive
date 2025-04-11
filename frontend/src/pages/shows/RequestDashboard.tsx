import 'chart.js/auto';
import React, { useEffect, useRef, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import { useAuth } from '../../contexts/AuthContext';
import { Show } from '../../models/show';
import { Song } from '../../models/song';
import { default as RequestService } from '../../services/request';
import './RequestDashboard.css';

const RequestDashboard: React.FC = () => {
    const [shows, setShows] = useState<Show[]>([]);
    const [songs, setSongs] = useState<Song[]>([]);
    const [selectedShow, setSelectedShow] = useState<Show | null>(null);
    const [songRequestCounts, setSongRequestCounts] = useState<any[]>([]);
    const [loading, setLoading] = useState<boolean>(false);
    const [syncing, setSyncing] = useState<boolean>(false);
    const { token } = useAuth();
    const chartRef = useRef<any>(null);

    useEffect(() => {
        const fetchData = async () => {
            setLoading(true);
            try {
                const shows = await RequestService.getRows('shows', token);
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

    const handleShowChange = async (show: Show) => {
        setSelectedShow(show);
        setLoading(true);
        try {
            const data = await RequestService.getCountOfRequestsByShowId(
                show.id
            );
            setSongRequestCounts(data);
        } catch (error) {
            console.error('Error fetching song request counts:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleSync = async () => {
        if (!selectedShow) return;
        setSyncing(true);
        try {
            const data = await RequestService.getCountOfRequestsByShowId(
                selectedShow.id
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

    const primary_color = getComputedStyle(document.documentElement)
        .getPropertyValue('--color-primary')
        .trim();

    const primary_color_opacity = getComputedStyle(
        document.documentElement
    ).getPropertyValue('--color-primary-opacity');

    const accent_color = getComputedStyle(
        document.documentElement
    ).getPropertyValue('--color-accent');

    const barChartData = {
        labels: songRequestCounts.map((item: any) => {
            const song = songs.find((s: any) => s.id === item.song_id);
            return song ? [song.band_name, song.song_name] : 'Unknown';
        }),
        datasets: [
            {
                data: songRequestCounts.map((item: any) => item.count),
                backgroundColor: accent_color,
                borderColor: primary_color,
                borderWidth: 1,
            },
        ],
    };

    const options = {
        scales: {
            x: {
                ticks: {
                    color: primary_color_opacity,
                    font: {
                        size: 18,
                    },
                },
            },
            y: {
                ticks: {
                    color: primary_color_opacity,
                    stepSize: 1,
                    beginAtZero: true,
                },
            },
        },
        plugins: {
            legend: {
                display: false,
            },
        },
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
                            (show) => show.id === e.target.value
                        );
                        if (selectedShow) {
                            handleShowChange(selectedShow);
                        }
                    }}
                    disabled={loading}
                >
                    <option value="">-- Select a Show --</option>
                    {shows.map((show) => (
                        <option key={show.id} value={show.id}>
                            {`${show.venue} - ${new Date(
                                show.start_time
                            ).toLocaleString()}`}
                        </option>
                    ))}
                </select>
                <button id="syncButton" onClick={handleSync} disabled={syncing}>
                    {syncing ? 'Syncing...' : 'Sync'}
                </button>
            </div>

            {selectedShow && songRequestCounts.length > 0 && (
                <div style={{ marginTop: 20 }}>
                    <Bar ref={chartRef} data={barChartData} options={options} />
                </div>
            )}
        </div>
    );
};

export default RequestDashboard;
