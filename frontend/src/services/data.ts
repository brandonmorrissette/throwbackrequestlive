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
    async getTableNames(): Promise<string[]> {
        const response = await apiRequest(`${API_BASE_URL}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table names');
        }
        return response.json();
    }

    async getTable(tableName: string): Promise<any> {
        const response = await apiRequest(`${API_BASE_URL}/${tableName}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table');
        }

        const table = await response.json();

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

        console.log('DataService::getTable::Properties:', table);
        return new Options(table.name, columns, primaryKeys, table);
    }

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

        console.log('DataService::readRows', tableName);
        const response = await apiRequest(
            `${API_BASE_URL}/${tableName}/rows?${queryParams.toString()}`
        );
        if (!response.ok) {
            throw new Error('Failed to fetch table data');
        }
        const rows = await response.json();
        console.log('DataService::readRows::rows', rows);
        return rows;
    }

    async writeRows(tableName: string, rows: any[]): Promise<void> {
        console.log('DataService::writeRows', tableName);
        const response = await apiRequest(`${API_BASE_URL}/${tableName}/rows`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ rows }),
        });
        if (!response.ok) {
            throw new Error('Failed to write table data');
        }
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
