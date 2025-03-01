import jwtDecode from 'jwt-decode';
import React from 'react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    redirectTo: string;
}

/**
 * ProtectedRoute component to protect routes based on JWT token.
 *
 * @param {Object} props - Component props.
 * @param {React.ReactNode} props.children - The child components to render if authenticated.
 * @param {string} props.redirectTo - The URL to redirect to if not authenticated.
 * @returns {React.ReactNode|null} The child components or null if not authenticated.
 */
const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
    children,
    redirectTo,
}) => {
    const token = sessionStorage.getItem('auth_token');

    if (!token) {
        window.location.href = redirectTo;
        return null;
    }

    try {
        const decodedToken: any = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
            window.location.href = redirectTo;
            return null;
        }
    } catch (error) {
        window.location.href = redirectTo;
        return null;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
