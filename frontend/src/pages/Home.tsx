import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Modal from '../components/app/modal/Modal';
import Shows from '../components/pages/home/Shows';
import ThankYou from '../components/pages/home/ThankYou'; // Import the ThankYou component

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
