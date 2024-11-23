import React from 'react';
import styles from './Content.module.css';

const Content: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return <main className={styles['container']}>{children}</main>;
};

export default Content;
