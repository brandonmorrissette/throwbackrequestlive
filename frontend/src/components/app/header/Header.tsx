import React from 'react';
import { Link } from 'react-router-dom';
import logo from '../../../assets/logo.jpg';
import styles from './Header.module.css';

const Header: React.FC = () => {
    return (
        <header>
            <nav
                className={`navbar navbar-expand-lg navbar-dark bg-dark ${styles.navbar}`}
            >
                <Link
                    className={`navbar-brand ${styles['navbar-brand']}`}
                    to="/"
                >
                    <img
                        src={logo}
                        alt="Throwback Request Live"
                        className={styles.logo}
                    />
                </Link>
            </nav>
        </header>
    );
};

export default Header;
