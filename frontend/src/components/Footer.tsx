import React, { useState } from 'react';
import Book from './Book';
import Tip from './Tip';
import styles from './Footer.module.css'; // Import your CSS module

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
        <footer className={styles.footer}>
            <button onClick={handleOpenTip} className="button">
                Tip
            </button>
            <button onClick={handleOpenBook} className="button">
                Book
            </button>
            {isTipOpen && <Tip onClose={handleCloseTip} />}
            {isBookOpen && <Book onClose={handleCloseBook} />}
        </footer>
    );
};

export default Footer;
