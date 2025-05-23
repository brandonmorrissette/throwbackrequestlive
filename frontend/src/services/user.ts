import { ColDef } from '../components/table/ColDef';
import { Options } from '../components/table/Options';
import apiRequest, { createBearerHeader } from '../routing/Request';
import { IDataService } from './data';

class UserService implements IDataService {
    /**
     * Fetches the user table schema.
     * @param {string} tableName - The name of the table.
     * @returns {Promise<any>} The table schema.
     */
    async getTableProperties(tableName: string): Promise<any> {
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

    /**
     * Reads user rows from the table.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @returns {Promise<any>} The user rows.
     */
    async getRows(tableName: string, token: string | null): Promise<any> {
        const data = await apiRequest(
            `/api/${tableName}`,
            createBearerHeader(token)
        );

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

    /**
     * Writes user rows to the table.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @param {any[]} rows - The rows to be written.
     * @returns {Promise<void>}
     * @throws {Error} If the request fails.
     */
    async putRows(
        tableName: string,
        token: string | null,
        rows: any[]
    ): Promise<void> {
        const response = await apiRequest(`/api/${tableName}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                ...createBearerHeader(token).headers,
            },
            body: JSON.stringify({ rows }),
        });
        if (!response.ok) {
            throw new Error('Failed to write user data');
        }
    }
}

export default new UserService();
