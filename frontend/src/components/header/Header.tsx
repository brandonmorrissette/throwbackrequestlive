import jwtDecode from 'jwt-decode';
import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import logo from '../../assets/logo.jpg';
import { useAuth } from '../../contexts/AuthContext'; // Import AuthContext
import styles from './Header.module.css';

const Header: React.FC = () => {
    const { token } = useAuth();
    const [showRestricted, setShowRestricted] = useState(false);

    const isTokenValid = (token: string | null) => {
        if (!token) return false;
        try {
            const decodedToken: any = jwtDecode(token);
            const currentTime = Date.now() / 1000;
            return decodedToken.exp > currentTime;
        } catch (error) {
            return false;
        }
    };

    useEffect(() => {
        setShowRestricted(isTokenValid(token));
    }, [token]);

    return (
        <header className={styles.header}>
            <nav
                className={`navbar navbar-expand-lg navbar-dark ${styles.navbar}`}
            >
                <div className="container-fluid">
                    {showRestricted && (
                        <button
                            className="navbar-toggler"
                            type="button"
                            data-bs-toggle="collapse"
                            data-bs-target="#navbarNav"
                            aria-controls="navbarNav"
                            aria-expanded="false"
                            aria-label="Toggle navigation"
                        >
                            <span className="navbar-toggler-icon"></span>
                        </button>
                    )}
                    <div className="collapse navbar-collapse" id="navbarNav">
                        {showRestricted && (
                            <ul className={`navbar-nav ${styles.headerNav}`}>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/shows">
                                        Manage Shows
                                    </Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/data">
                                        Manage Data
                                    </Link>
                                </li>
                                <li className="nav-item">
                                    <Link className="nav-link" to="/users">
                                        Manage Users
                                    </Link>
                                </li>
                            </ul>
                        )}
                    </div>
                </div>
            </nav>
            <Link to="/" className={styles.logoContainer}>
                <img
                    src={logo}
                    alt="Throwback Request Live"
                    className={styles.logo}
                />
            </Link>
        </header>
    );
};

export default Header;
