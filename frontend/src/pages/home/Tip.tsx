import React from 'react';
import Modal from '../../components/modal/Modal';

interface TipProps {
    onClose: () => void;
}

/**
 * Tip component that displays a modal with an embedded tip page.
 * @component
 * @param {TipProps} props - The properties for the Tip component.
 * @param {() => void} props.onClose - Function to close the modal.
 */
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
