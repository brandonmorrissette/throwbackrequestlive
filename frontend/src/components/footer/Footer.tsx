import React, { useState } from 'react';
import Book from '../../pages/home/Book';
import Tip from '../../pages/home/Tip';
import styles from './Footer.module.css';

/**
 * Footer component that displays buttons to open Tip and Book modals.
 * @returns {JSX.Element} The rendered component.
 */
const Footer: React.FC = () => {
    const [isTipOpen, setIsTipOpen] = useState(false);
    const [isBookOpen, setIsBookOpen] = useState(false);

    /**
     * Opens the Tip modal.
     */
    const handleOpenTip = () => {
        setIsTipOpen(true);
    };

    /**
     * Closes the Tip modal.
     */
    const handleCloseTip = () => {
        setIsTipOpen(false);
    };

    /**
     * Opens the Book modal.
     */
    const handleOpenBook = () => {
        setIsBookOpen(true);
    };

    /**
     * Closes the Book modal.
     */
    const handleCloseBook = () => {
        setIsBookOpen(false);
    };

    return (
        <footer className={`${styles.footer} button-group`}>
            <button onClick={handleOpenTip}>Tip</button>
            <button onClick={handleOpenBook}>Book</button>
            {isTipOpen && <Tip onClose={handleCloseTip} />}
            {isBookOpen && <Book onClose={handleCloseBook} />}
        </footer>
    );
};

export default Footer;
