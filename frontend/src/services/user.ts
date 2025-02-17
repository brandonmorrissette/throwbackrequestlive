import { ColDef } from '../components/table/ColDef';
import { Options } from '../components/table/Options';
import apiRequest from '../routing/Request';
import { IDataService } from './data';

class UserService implements IDataService {
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
        return new Options(tableName, columns, primaryKeys);
    }

    async readRows(tableName: string): Promise<any> {
        const data = await apiRequest(`/api/${tableName}`);

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
        const response = await apiRequest(`/api/${tableName}`, {
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
