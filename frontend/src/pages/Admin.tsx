import React, { useEffect, useState } from 'react';

const Admin: React.FC = () => {
    const [userGroups, setUserGroups] = useState<string[]>([]);

    useEffect(() => {
        const token = sessionStorage.getItem('auth_token');
        const groups = sessionStorage.getItem('user_groups');

        if (token) {
            setUserGroups(groups ? JSON.parse(groups) : []);
        } else {
            window.location.href = '/login';
        }
    }, []);

    const renderAdminContent = () => {
        if (userGroups.includes('admin')) {
            return <div>Admin Content</div>;
        } else if (userGroups.includes('superuser')) {
            return <div>Superuser Content</div>;
        } else {
            return <div>You do not have permission to access this page</div>;
        }
    };

    return (
        <div>
            <h1>Admin Dashboard</h1>
            {renderAdminContent()}
        </div>
    );
};

export default Admin;
