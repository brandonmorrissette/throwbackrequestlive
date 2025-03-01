import React from 'react';
import styles from './Content.module.css';

/**
 * Props for the Content component.
 * @property {string} [className] - Optional additional class name(s) to apply to the content.
 * @property {React.ReactNode} children - The content to be displayed within the component.
 */
interface ContentProps {
    className?: string;
    children: React.ReactNode;
}

/**
 * A functional component that wraps its children with a styled div.
 * @param {ContentProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const Content: React.FC<ContentProps> = ({ className, children }) => {
    const contentClass = className
        ? `${styles.content} ${styles[className]}`
        : styles.content;
    return <div className={contentClass}>{children}</div>;
};

export default Content;
