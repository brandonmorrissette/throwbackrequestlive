import jwtDecode from 'jwt-decode';
import React from 'react';

interface ProtectedRouteProps {
    children: React.ReactNode;
    redirectTo: string;
}

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
