import React from 'react';
import styles from './Modal.module.css';

interface ModalProps {
    children: React.ReactNode;
    onClose: () => void;
}

const Modal: React.FC<ModalProps> = ({ children, onClose }) => {
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
