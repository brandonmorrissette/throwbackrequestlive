import { ColDef } from '../components/table/ColDef';
import { Options } from '../components/table/Options';
import apiRequest from '../routing/Request';

const API_BASE_URL = '/api/tables';

export interface IDataService {
    getTable(tableName: string): Promise<any>;
    readRows(tableName: string): Promise<any[]>;
    writeRows(tableName: string, rows: any[]): Promise<void>;
}

class DataService implements IDataService {
    /**
     * Fetches the list of table names.
     * @returns {Promise<string[]>} The list of table names.
     */
    async getTableNames(): Promise<string[]> {
        return await apiRequest(`${API_BASE_URL}`);
    }

    /**
     * Fetches the table schema and data.
     * @param {string} tableName - The name of the table.
     * @returns {Promise<any>} The table schema and data.
     */
    async getTable(tableName: string): Promise<any> {
        const table = await apiRequest(`${API_BASE_URL}/${tableName}`);

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
     * @param {Object} [options] - Optional parameters for filtering, limiting, offsetting, and sorting.
     * @returns {Promise<any>} The table rows.
     */
    async readRows(
        tableName: string,
        options?: {
            filters?: string[];
            limit?: number;
            offset?: number;
            sort_by?: string;
            sort_order?: 'asc' | 'desc';
        }
    ): Promise<any> {
        const queryParams = new URLSearchParams();

        if (options?.filters)
            queryParams.append('filters', JSON.stringify(options.filters));
        if (options?.limit)
            queryParams.append('limit', JSON.stringify(options.limit));
        if (options?.offset)
            queryParams.append('offset', JSON.stringify(options.offset));
        if (options?.sort_by) queryParams.append('sort_by', options.sort_by);
        if (options?.sort_order)
            queryParams.append('sort_order', options.sort_order);

        return await apiRequest(
            `${API_BASE_URL}/${tableName}/rows?${queryParams.toString()}`
        );
    }

    /**
     * Writes rows to the table.
     * @param {string} tableName - The name of the table.
     * @param {any[]} rows - The rows to be written.
     * @returns {Promise<void>}
     */
    async writeRows(tableName: string, rows: any[]): Promise<void> {
        await apiRequest(`${API_BASE_URL}/${tableName}/rows`, {
            method: 'PUT',
            headers: {
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
