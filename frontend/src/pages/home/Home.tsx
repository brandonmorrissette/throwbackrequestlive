import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import Modal from '../../components/modal/Modal';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import { default as DataService } from '../../services/data';
import Shows from './Shows';
import ThankYou from './ThankYou';

/**
 * Home component that displays the home page with shows and a thank you modal.
 * @component
 */
const Home: React.FC = () => {
    const location = useLocation();
    const params = new URLSearchParams(location.search);
    const song = params.get('song');

    const [showModal, setShowModal] = useState(!!song);

    return (
        <div>
            <TableServiceProvider service={DataService}>
                <Shows />
            </TableServiceProvider>
            {showModal && song && (
                <Modal onClose={() => setShowModal(false)}>
                    <ThankYou song={song} />
                </Modal>
            )}
        </div>
    );
};

export default Home;
