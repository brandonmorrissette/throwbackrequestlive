import jwtDecode from 'jwt-decode';
import React, { useEffect, useState } from 'react';

const Admin: React.FC = () => {
    const [userGroups, setUserGroups] = useState<string[]>([]);

    useEffect(() => {
        const token = sessionStorage.getItem('auth_token');

        if (token) {
            try {
                const decodedToken: any = jwtDecode(token);
                setUserGroups(decodedToken.groups || []);
            } catch (e) {
                console.error('Invalid token', e);
                window.location.href = '/login';
            }
        } else {
            window.location.href = '/login';
        }
    }, []);

    const renderContent = () => {
        const content = (
            <div>
                {userGroups.includes('admin') && (
                    <div>
                        <h3>Admin Content</h3>
                        <p>Content for Admin group</p>
                    </div>
                )}
                {userGroups.includes('superuser') && (
                    <div>
                        <h3>Superuser Content</h3>
                        <p>Content for Superuser group</p>
                    </div>
                )}
            </div>
        );

        if (content.props.children && content.props.children.length === 0) {
            return (
                <p>No content to display for groups: {userGroups.join(', ')}</p>
            );
        }

        return content;
    };

    return (
        <div>
            <h1>Admin Dashboard</h1>
            {renderContent()}
        </div>
    );
};

export default Admin;
