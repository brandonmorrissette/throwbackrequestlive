import React from 'react';
import styles from './Modal.module.css';

/**
 * Props for the Modal component.
 * @property {React.ReactNode} children - The content to be displayed within the modal.
 * @property {() => void} onClose - Function to call when the modal is closed.
 */
interface ModalProps {
    children: React.ReactNode;
    onClose: () => void;
}

/**
 * A functional component that displays a modal with an overlay.
 * @param {ModalProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const Modal: React.FC<ModalProps> = ({ children, onClose }) => {
    /**
     * Handles the overlay click event to close the modal.
     * @param {React.MouseEvent<HTMLDivElement>} e - The click event.
     */
    const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
        if (e.target === e.currentTarget) {
            onClose();
        }
    };

    return (
        <div className={styles.overlay} onClick={handleOverlayClick}>
            <div className={styles.modal}>
                {children}
                <p className={styles['close-instruction']}>
                    Click anywhere outside the box to close
                </p>
            </div>
        </div>
    );
};

export default Modal;
