import React from 'react';
import Modal from '../../components/modal/Modal';
import { Show } from './Shows';

interface ShowDetailProps {
    show: Show;
    onClose: () => void;
}

const ShowDetail: React.FC<ShowDetailProps> = ({ show, onClose }) => {
    const addressParts = [show.street, show.city, show.state].filter(Boolean);
    const address = addressParts.join(', ');
    const mapsLink = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
        address
    )}`;

    const formatDateTime = (datetime: string) => {
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
    };

    return (
        <Modal onClose={onClose}>
            <h2 className="modal-title">{show.name}</h2>
            <p>
                <strong>When:</strong> {formatDateTime(show.datetime)}
            </p>
            <p>
                <strong>Where:</strong> {show.venue}
            </p>
            {address && (
                <p>
                    <strong>Address:</strong>{' '}
                    <a
                        href={mapsLink}
                        target="_blank"
                        rel="noopener noreferrer"
                    >
                        {address}
                    </a>
                </p>
            )}
        </Modal>
    );
};

export default ShowDetail;
