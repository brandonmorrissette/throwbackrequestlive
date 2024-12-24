import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Modal from '../../components/modal/Modal';
import Shows from './Shows';
import ThankYou from './ThankYou';

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
                    <ThankYou song={song} />
                </Modal>
            )}
        </div>
    );
};

export default Home;
