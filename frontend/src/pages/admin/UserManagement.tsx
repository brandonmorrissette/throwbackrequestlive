import { useEffect, useState } from 'react';
import Table from '../../components/table/Table';
import { useError } from '../../contexts/ErrorContext';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import {
    default as UserService,
    default as userService,
} from '../../services/user';
import { AdminComponent } from './Admin';

type User = {
    username: string;
    email: string;
    groups: string[];
};

const UserManagement: AdminComponent = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [table, setTable] = useState<any>({});
    const [feedback, setFeedback] = useState('');
    const { setError } = useError();

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
        } catch (error: any) {
            setFeedback('Error fetching table properties.');
            setError(error);
        }
    };

    const fetchUsersData = async () => {
        try {
            const data = await UserService.readRows('users');
            setUsers(data);
        } catch (error: any) {
            setFeedback('Error fetching users.');
            setError(error);
        }
    };

    return (
        <div>
            <h1>User Management</h1>
            {feedback && <p>{feedback}</p>}

            <TableServiceProvider service={userService}>
                <Table options={table} data={users} />
            </TableServiceProvider>
        </div>
    );
};

UserManagement.allowed_groups = ['supergroup'];

export default UserManagement;
