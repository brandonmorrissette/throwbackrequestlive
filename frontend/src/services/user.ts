import { ColDef, Properties } from '../components/table/Table';
import apiRequest from '../routing/Request';
import { TableService } from './tableService';

class UserService implements TableService {
    async getTable(tableName: string): Promise<any> {
        const columns = [
            new ColDef({
                field: 'Username',
                headerName: 'Username',
                sortable: true,
            }),
            new ColDef({
                field: 'Email',
                headerName: 'Email',
                editable: true,
                sortable: true,
            }),
            new ColDef({
                field: 'Groups',
                headerName: 'Groups',
                sortable: true,
            }),
            new ColDef({
                field: 'UserCreateDate',
                headerName: 'UserCreateDate',
                sortable: true,
            }),
            new ColDef({
                field: 'UserLastModifiedDate',
                headerName: 'UserLastModifiedDate',
                sortable: true,
            }),
            new ColDef({
                field: 'Enabled',
                headerName: 'Enabled',
                editable: true,
                sortable: true,
            }),
            new ColDef({
                field: 'UserStatus',
                headerName: 'Status',
                sortable: true,
            }),
            new ColDef({
                field: 'Attributes',
                headerName: 'Attributes',
            }),
        ];

        const primaryKeys = [
            new ColDef({ field: 'Username', headerName: 'Username' }),
        ];
        return new Properties(tableName, columns, primaryKeys);
    }

    async readRows(tableName: string): Promise<any> {
        console.info('UserService::readRows', tableName);
        const response = await apiRequest('/api/users');
        if (!response.ok) {
            throw new Error('Failed to fetch user data');
        }
        const data = await response.json();
        const transformed = data.map((user: any) => {
            const email = user.Attributes.find(
                (attr: any) => attr.Name === 'email'
            )?.Value;

            const attributes = user.Attributes.map((attr: any) =>
                JSON.stringify(attr)
            );

            const transformedUser = {
                ...user,
                Email: email,
                Attributes: attributes,
            };
            return transformedUser;
        });
        return transformed;
    }

    async writeRows(tableName: string, rows: any[]): Promise<void> {
        console.info('UserService::writeRows', tableName);
        const response = await apiRequest('/api/users', {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rows }),
        });
        if (!response.ok) {
            throw new Error('Failed to write user data');
        }
    }
}

export default new UserService();
