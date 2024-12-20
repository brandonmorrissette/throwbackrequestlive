import apiRequest from '../components/routing/Request';

const API_BASE_URL = '/api/tables';

export const getTableNames = async (): Promise<string[]> => {
    const response = await apiRequest(`${API_BASE_URL}`);
    if (!response.ok) {
        throw new Error('Failed to fetch table names');
    }
    return response.json();
};

export const getRows = async (tableName: string): Promise<any[]> => {
    const response = await apiRequest(`${API_BASE_URL}/${tableName}`);
    if (!response.ok) {
        throw new Error('Failed to fetch table data');
    }
    return response.json();
};

export const getColumns = async (tableName: string): Promise<any[]> => {
    const response = await apiRequest(`${API_BASE_URL}/${tableName}/columns`);
    if (!response.ok) {
        throw new Error('Failed to fetch column definitions');
    }
    return response.json();
};

export const writeRows = async (
    tableName: string,
    rows: any[]
): Promise<void> => {
    console.log('writeRows', tableName, rows);
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
};
