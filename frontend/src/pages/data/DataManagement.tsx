import { useEffect, useState } from 'react';
import { Options } from '../../components/table/Options';
import Table from '../../components/table/Table';
import TableSelector from '../../components/table/TableSelector';
import { useAuth } from '../../contexts/AuthContext';
import { useError } from '../../contexts/ErrorContext';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import { default as DataService } from '../../services/data';

/**
 * DataManagement component that allows managing data tables.
 * @component
 */
const DataManagement: React.FC = () => {
    const [tables, setTables] = useState<string[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableProperties, setTableProperties] = useState<Options>(
        new Options('', [], [], [], [], [])
    );
    const [rows, setRows] = useState<any[]>([]);
    const { setError } = useError();
    const { token } = useAuth();

    useEffect(() => {
        fetchTableNames();
    }, []);

    useEffect(() => {
        if (selectedTable) {
            fetchData(selectedTable);
        }
    }, [selectedTable]);

    const fetchTableNames = async () => {
        try {
            setTables(await DataService.getTableNames(token));
        } catch (error: any) {
            console.error('Error fetching table names:', error);
            setError(error);
        }
    };

    const fetchData = async (tableName: string) => {
        try {
            const properties = await DataService.getTableProperties(
                tableName,
                token
            );
            setTableProperties(properties);

            const rows = await DataService.getRows(tableName, token);
            setRows(rows);
        } catch (error: any) {
            console.error('Error fetching table or rows:', error);
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

export default DataManagement;
