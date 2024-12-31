import { ColDef, Properties } from '../components/table/Table';
import apiRequest from '../routing/Request';
import { TableService } from './tableService';

const API_BASE_URL = '/api/tables';

const mapType = (backendType: string): string => {
    switch (backendType.toUpperCase()) {
        case 'INTEGER':
        case 'SMALLINT':
        case 'BIGINT':
        case 'SERIAL':
        case 'BIGSERIAL':
        case 'DECIMAL':
        case 'NUMERIC':
        case 'REAL':
        case 'DOUBLE PRECISION':
            return 'number';
        case 'DATE':
        case 'TIMESTAMP':
        case 'TIMESTAMPTZ':
        case 'TIME':
        case 'TIMETZ':
            return 'dateString';
        case 'BOOLEAN':
            return 'boolean';
        case 'TEXT':
        case 'CHAR':
        case 'VARCHAR':
        case 'UUID':
        case 'JSON':
        case 'JSONB':
        case backendType.match(/^VARCHAR/i) ? backendType : '':
            return 'text';
        default:
            return 'object';
    }
};

const timestampFormatter = (params: any) => {
    const date = new Date(params.value);
    return date.toLocaleString();
};

class DataService implements TableService {
    async getTableNames(): Promise<string[]> {
        const response = await apiRequest(`${API_BASE_URL}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table names');
        }
        return response.json();
    }

    async getTable(tableName: string): Promise<any> {
        console.log('DataService::getTable', tableName);
        const response = await apiRequest(`${API_BASE_URL}/${tableName}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table');
        }

        const table = await response.json();
        console.log('DataService::getTable', table);

        const columns: ColDef[] = table.columns.map((col: any) => {
            const columnDef: ColDef = {
                field: col.name,
                headerName: col.name,
                editable: true,
                sortable: true,
                cellDataType: mapType(col.type),
            };

            if (columnDef.cellDataType === 'dateString') {
                columnDef.valueFormatter = timestampFormatter;
            }

            return columnDef;
        });

        const primaryKeys: ColDef[] = table.primary_key.map((key: any) => ({
            field: key.name,
            headerName: key.name,
        }));

        return new Properties(table.name, columns, primaryKeys, table);
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
        return response.json();
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
