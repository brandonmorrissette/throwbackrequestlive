import React, { useState } from 'react';
import Book from '../../pages/home/Book';
import Tip from '../../pages/home/Tip';
import styles from './Footer.module.css';

const Footer: React.FC = () => {
    const [isTipOpen, setIsTipOpen] = useState(false);
    const [isBookOpen, setIsBookOpen] = useState(false);

    const handleOpenTip = () => {
        setIsTipOpen(true);
    };

    const handleCloseTip = () => {
        setIsTipOpen(false);
    };

    const handleOpenBook = () => {
        setIsBookOpen(true);
    };

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
