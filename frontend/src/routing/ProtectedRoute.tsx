import jwtDecode from 'jwt-decode';
import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

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
    const { token } = useAuth();
    const navigate = useNavigate();

    useEffect(() => {
        if (!token) {
            navigate(redirectTo);
        } else {
            try {
                const decodedToken: any = jwtDecode(token);
                const currentTime = Date.now() / 1000;

                if (decodedToken.exp < currentTime) {
                    navigate(redirectTo);
                }
            } catch (error) {
                navigate(redirectTo);
            }
        }
    }, [token, navigate, redirectTo]);

    if (!token) {
        return null;
    }

    try {
        const decodedToken: any = jwtDecode(token);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
            return null;
        }
    } catch (error) {
        return null;
    }

    return <>{children}</>;
};

export default ProtectedRoute;
