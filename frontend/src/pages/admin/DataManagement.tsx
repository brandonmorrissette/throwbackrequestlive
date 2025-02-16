import { useEffect, useState } from 'react';
import Table from '../../components/table/Table';
import TableSelector from '../../components/table/TableSelector';
import { useError } from '../../contexts/ErrorContext';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import { default as DataService } from '../../services/data';
import { AdminComponent } from './Admin';

const DataManagement: AdminComponent = () => {
    const [tables, setTables] = useState<string[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableProperties, setTableProperties] = useState<any>({});
    const [rows, setRows] = useState<any[]>([]);
    const { setError } = useError();

    useEffect(() => {
        fetchTableNames();
    }, []);

    useEffect(() => {
        if (selectedTable) {
            fetchTable(selectedTable);
            fetchRows(selectedTable);
        }
    }, [selectedTable]);

    const fetchTableNames = async () => {
        try {
            const data = await DataService.getTableNames();
            setTables(data);
        } catch (error: any) {
            console.error('Error fetching table names:', error);
            setError(error);
        }
    };

    const fetchTable = async (tableName: string) => {
        try {
            const data = await DataService.getTable(tableName);
            setTableProperties(data);
        } catch (error: any) {
            console.error('Error fetching table properties:', error);
            setError(error);
        }
    };

    const fetchRows = async (tableName: string) => {
        try {
            const data = await DataService.readRows(tableName);
            setRows(data);
        } catch (error: any) {
            console.error('Error fetching rows:', error);
            setError(error);
        }
    };

    return (
        <div>
            <h1>Data Management</h1>
            <TableSelector tables={tables} onSelectTable={setSelectedTable} />
            {selectedTable && (
                <TableServiceProvider service={DataService}>
                    <Table options={tableProperties} data={rows} />
                </TableServiceProvider>
            )}
        </div>
    );
};

DataManagement.allowed_groups = ['superuser'];

export default DataManagement;
