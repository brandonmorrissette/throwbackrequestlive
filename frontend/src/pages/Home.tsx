import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Modal from '../components/Modal';
import Shows from '../components/Shows';
import ThankYou from '../components/ThankYou'; // Import the ThankYou component

const Home: React.FC = () => {
    const location = useLocation();
    const params = new URLSearchParams(location.search);
    const song = params.get('song');

    const [showModal, setShowModal] = useState(!!song);

    return (
        <div>
            <Shows />
            {showModal && song && (
                <Modal onClose={() => setShowModal(false)}>
                    <ThankYou song={song} /> {/* Use the ThankYou component */}
                </Modal>
            )}
        </div>
    );
};

export default Home;
