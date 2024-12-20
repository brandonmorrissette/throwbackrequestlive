import React, { useEffect, useState } from 'react';
import { fetchUsers } from '../../../services/user';
import Table from './Table';

type User = {
    username: string;
    email: string;
    groups: string[];
};

const UserManagement: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [feedback, setFeedback] = useState('');
    const columnDefs = [
        { headerName: 'Username', field: 'username' },
        { headerName: 'Email', field: 'email' },
        { headerName: 'Groups', field: 'groups' },
    ];

    useEffect(() => {
        fetchUsersData();
    }, []);

    const fetchUsersData = async () => {
        try {
            const data = await fetchUsers();
            setUsers(data);
        } catch (error) {
            setFeedback('Error fetching users.');
        }
    };

    return (
        <div>
            <h1>User Management</h1>
            {feedback && <p>{feedback}</p>}
            <Table table_name="Users" data={users} columns={columnDefs} />
        </div>
    );
};

export default UserManagement;
