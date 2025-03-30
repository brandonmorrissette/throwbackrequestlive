import jwtDecode from 'jwt-decode';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DataManagement from './DataManagement';
import UserManagement from './UserManagement';

export interface AdminComponent extends React.FC {
    allowed_groups?: string[];
}

/**
 * Admin component that renders user and data management components based on user groups.
 * @component
 */
const Admin: React.FC = () => {
    const [userGroups, setUserGroups] = useState<string[]>([]);

    const navigate = useNavigate();

    useEffect(() => {
        const token = sessionStorage.getItem('auth_token');

        if (token) {
            try {
                const decodedToken: any = jwtDecode(token);
                const groups = decodedToken.groups || [];
                console.log('User groups:', groups);
                setUserGroups(groups);
            } catch (e) {
                console.error('Invalid token', e);
                navigate('/login');
            }
        } else {
            navigate('/login');
        }
    }, []);

    const renderContent = () => {
        const content = (
            <div>
                {userGroups.some((element) =>
                    UserManagement.allowed_groups?.includes(element)
                ) && (
                    <div>
                        <UserManagement />
                        <hr />
                    </div>
                )}
                {userGroups.some((element) =>
                    DataManagement.allowed_groups?.includes(element)
                ) && (
                    <div>
                        <DataManagement />
                        <hr />
                    </div>
                )}
            </div>
        );

        console.log('Content:', content);
        if (
            content.props.children &&
            content.props.children.every((child: React.ReactNode) => !child)
        ) {
            if (userGroups.length === 0) {
                return <p>User has no groups.</p>;
            }

            return (
                <p>No content to display for groups: {userGroups.join(', ')}</p>
            );
        }

        return content;
    };

    return renderContent();
};

export default Admin;
