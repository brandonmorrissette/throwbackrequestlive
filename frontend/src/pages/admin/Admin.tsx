import jwtDecode from 'jwt-decode';
import React, { useEffect, useState } from 'react';
import DataManagement from './DataManagement';
import UserManagement from './UserManagement';

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
                {userGroups.includes('superuser') && (
                    <div>
                        <UserManagement />
                        <hr />
                    </div>
                )}
                {userGroups.includes('admin') && (
                    <div>
                        <DataManagement />
                        <hr />
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

    return renderContent();
};

export default Admin;
