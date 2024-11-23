import React, { useState } from 'react';
import Book from './Book';
import styles from './Footer.module.css';
import Tip from './Tip';

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
