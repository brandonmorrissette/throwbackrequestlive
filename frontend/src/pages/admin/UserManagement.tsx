import React, { useEffect, useState } from 'react';
import Table from '../../components/table/Table';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import {
    default as UserService,
    default as userService,
} from '../../services/user';

type User = {
    username: string;
    email: string;
    groups: string[];
};

const UserManagement: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [table, setTable] = useState<any>({});
    const [feedback, setFeedback] = useState('');

    useEffect(() => {
        fetchTable();
    }, []);

    useEffect(() => {
        fetchUsersData();
    }, []);

    const fetchTable = async () => {
        try {
            const data = await UserService.getTable('users');
            setTable(data);
        } catch (error) {
            setFeedback('Error fetching table properties.');
        }
    };

    const fetchUsersData = async () => {
        try {
            const data = await UserService.readRows('users');
            setUsers(data);
        } catch (error) {
            setFeedback('Error fetching users.');
        }
    };

    return (
        <div>
            <h1>User Management</h1>
            {feedback && <p>{feedback}</p>}

            <TableServiceProvider service={userService}>
                <Table properties={table} data={users} />
            </TableServiceProvider>
        </div>
    );
};

export default UserManagement;
