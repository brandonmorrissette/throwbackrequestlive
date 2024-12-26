import { ColumnDef, Properties } from '../components/table/Table';
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
            return 'date';
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

class DataService implements TableService {
    async getTableNames(): Promise<string[]> {
        const response = await apiRequest(`${API_BASE_URL}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table names');
        }
        return response.json();
    }

    async getTableProperties(tableName: string): Promise<any> {
        const response = await apiRequest(
            `${API_BASE_URL}/${tableName}/properties`
        );
        if (!response.ok) {
            throw new Error('Failed to fetch table properties');
        }

        const properties = await response.json();
        console.log('DataService::getTableProperties', properties);

        const columns: ColumnDef[] = properties.columns.map((col: any) => ({
            field: col.name,
            headerName: col.name,
            editable: true,
            sortable: true,
            cellDataType: mapType(col.type),
        }));

        const primaryKeys: ColumnDef[] = properties.primary_key.map(
            (key: any) => ({
                field: key.name,
                headerName: key.name,
            })
        );

        return new Properties(
            properties.name,
            columns,
            primaryKeys,
            properties
        );
    }

    async readRows(tableName: string): Promise<any> {
        console.log('DataService::readRows', tableName);
        const response = await apiRequest(`${API_BASE_URL}/${tableName}`);
        if (!response.ok) {
            throw new Error('Failed to fetch table data');
        }
        return response.json();
    }

    async writeRows(tableName: string, rows: any[]): Promise<void> {
        console.log('DataService::writeRows', tableName);
        const response = await apiRequest(`${API_BASE_URL}/${tableName}`, {
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
