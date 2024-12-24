import React from 'react';
import styles from './Content.module.css';

interface ContentProps {
    className?: string;
    children: React.ReactNode;
}

const Content: React.FC<ContentProps> = ({ className, children }) => {
    const contentClass = className
        ? `${styles.content} ${styles[className]}`
        : styles.content;
    return <div className={contentClass}>{children}</div>;
};

export default Content;
