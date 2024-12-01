// src/pages/Admin.tsx
import React from 'react';
import UserManagement from '../components/pages/admin/UserManagement';
import LoginModal from '../components/pages/login/LoginModal';
import { useAuth } from '../context/AuthContext';

const Admin: React.FC = () => {
    const { isAuthenticated } = useAuth();

    if (!isAuthenticated) {
        return <LoginModal />;
    }

    return <UserManagement />;
};

export default Admin;
