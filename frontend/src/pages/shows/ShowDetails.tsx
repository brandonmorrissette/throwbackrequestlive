import React from 'react';
import Modal from '../../components/modal/Modal';
import { Show } from '../../models/show';

interface ShowDetailProps {
    show: Show;
    onClose: () => void;
}

/**
 * ShowDetail component that displays detailed information about a show in a modal.
 * @component
 * @param {ShowDetailProps} props - The properties for the ShowDetail component.
 * @param {Show} props.show - The show data.
 * @param {() => void} props.onClose - Function to close the modal.
 */
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
                <strong>When:</strong> {show.start_time}
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
