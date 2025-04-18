import { ColDef } from '../components/table/ColDef';
import { Options } from '../components/table/Options';
import apiRequest, { createBearerHeader } from '../routing/Request';

const API_BASE_URL = '/api/tables';

export interface IDataService {
    getTableProperties(tableName: string, token: string): Promise<any>;
    getRows(tableName: string, token: string): Promise<any[]>;
    putRows(tableName: string, token: string, rows: any[]): Promise<void>;
}

export class DataService implements IDataService {
    /**
     * Fetches the list of table names.
     * @param {string} token - The authentication token.
     * @returns {Promise<string[]>} The list of table names.
     */
    async getTableNames(token: string | null): Promise<string[]> {
        return await apiRequest(`${API_BASE_URL}`, createBearerHeader(token));
    }

    /**
     * Fetches the table schema and data.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @returns {Promise<any>} The table schema and data.
     */
    async getTableProperties(
        tableName: string,
        token: string | null
    ): Promise<Options> {
        const table = await apiRequest(
            `${API_BASE_URL}/${tableName}`,
            createBearerHeader(token)
        );

        const columns: ColDef[] = table.columns.map((col: any) => {
            const columnDef: ColDef = new ColDef({
                field: col.name,
                headerName: col.name,
                editable: !col.autoincrement,
                cellDataType: mapType(col.type),
                autoIncrement: col.autoincrement,
                ...col,
            });

            return columnDef;
        });

        const primaryKeys: ColDef[] = table.primary_key.map(
            (key: any) =>
                new ColDef({
                    field: key.name,
                    headerName: key.name,
                    ...key,
                })
        );

        return new Options(table.name, columns, primaryKeys, table);
    }

    /**
     * Reads rows from the table with optional filters, limit, offset, and sorting.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @returns {Promise<any>} The table rows.
     */
    async getRows(tableName: string, token: string | null): Promise<any> {
        return await apiRequest(
            `${API_BASE_URL}/${tableName}/rows`,
            createBearerHeader(token)
        );
    }

    /**
     * Puts rows in a table.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @param {any[]} rows - The rows to be written.
     * @returns {Promise<void>}
     */
    async putRows(
        tableName: string,
        token: string | null,
        rows: any[]
    ): Promise<void> {
        await apiRequest(`${API_BASE_URL}/${tableName}/rows`, {
            method: 'PUT',
            headers: {
                ...createBearerHeader(token).headers,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rows }),
        });
    }

    /**
     * Posts rows to a table.
     * @param {string} tableName - The name of the table.
     * @param {string} token - The authentication token.
     * @param {any[]} rows - The rows to be written.
     * @returns {Promise<void>}
     */
    async postRows(
        tableName: string,
        token: string | null,
        rows: any[]
    ): Promise<void> {
        await apiRequest(`${API_BASE_URL}/${tableName}/rows`, {
            method: 'POST',
            headers: {
                ...createBearerHeader(token).headers,
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rows }),
        });
    }
}

export default new DataService();

const mapType = (backendType: string): string => {
    switch (backendType) {
        case 'int':
        case 'float':
            return 'number';
        case 'datetime':
            return 'datetime';
        case 'bool':
            return 'boolean';
        case 'str':
            return 'text';
        default:
            return 'object';
    }
};
