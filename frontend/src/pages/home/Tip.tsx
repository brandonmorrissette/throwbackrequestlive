import React from 'react';
import Modal from '../../components/modal/Modal';

interface TipProps {
    onClose: () => void;
}

const Tip: React.FC<TipProps> = ({ onClose }) => {
    return (
        <Modal onClose={onClose}>
            <iframe
                src="https://tiptopjar.com/throwbackrequestlive"
                title="Tip Page"
                style={{
                    width: '90vw',
                    height: '80vh',
                    border: 0,
                }}
            ></iframe>
        </Modal>
    );
};

export default Tip;
