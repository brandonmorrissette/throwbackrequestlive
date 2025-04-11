import { useEffect, useState } from 'react';
import Table from '../../components/table/Table';
import { useAuth } from '../../contexts/AuthContext';
import { useError } from '../../contexts/ErrorContext';
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

/**
 * UserManagement component that displays a table of users and their details.
 * @component
 */
const UserManagement: React.FC = () => {
    const [users, setUsers] = useState<User[]>([]);
    const [table, setTable] = useState<any>({});
    const [feedback, setFeedback] = useState('');
    const { setError } = useError();
    const { token } = useAuth();

    useEffect(() => {
        fetchTable();
    }, []);

    useEffect(() => {
        fetchUsersData();
    }, []);

    const fetchTable = async () => {
        try {
            const data = await UserService.getTableProperties('users');
            setTable(data);
        } catch (error: any) {
            setFeedback('Error fetching table properties.');
            setError(error);
        }
    };

    const fetchUsersData = async () => {
        try {
            const data = await UserService.getRows('users', token);
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

export default UserManagement;
