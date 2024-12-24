import React from 'react';
import Modal from '../../components/modal/Modal';

interface Show {
    name: string;
    date: string;
    time: string;
    venue: string;
    street: string;
    city: string;
    state: string;
}

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

    return (
        <Modal onClose={onClose}>
            <h2 className="modal-title">{show.name}</h2>
            <p>
                <strong>Date:</strong> {show.date}
            </p>
            <p>
                <strong>Time:</strong> {show.time}
            </p>
            <p>
                <strong>Venue:</strong> {show.venue}
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
