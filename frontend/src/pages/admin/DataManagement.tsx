import React, { useEffect, useState } from 'react';
import Table from '../../components/table/Table';
import TableSelector from '../../components/table/TableSelector';
import { TableServiceProvider } from '../../contexts/TableServiceContext';
import {
    default as DataService,
    default as dataService,
} from '../../services/data';

const DataManagement: React.FC = () => {
    const [tables, setTables] = useState<string[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableProperties, setTableProperties] = useState<any>({});
    const [rows, setRows] = useState<any[]>([]);

    useEffect(() => {
        fetchTableNames();
    }, []);

    useEffect(() => {
        if (selectedTable) {
            fetchTableProperties(selectedTable);
            fetchRows(selectedTable);
        }
    }, [selectedTable]);

    const fetchTableNames = async () => {
        try {
            const data = await DataService.getTableNames();
            setTables(data);
        } catch (error) {
            console.error('Error fetching table names:', error);
        }
    };

    const fetchTableProperties = async (tableName: string) => {
        try {
            const data = await DataService.getTableProperties(tableName);
            setTableProperties(data);
        } catch (error) {
            console.error('Error fetching table properties:', error);
        }
    };

    const fetchRows = async (tableName: string) => {
        try {
            const data = await DataService.readRows(tableName);
            setRows(data);
        } catch (error) {
            console.error('Error fetching rows:', error);
        }
    };

    return (
        <div>
            <h1>Data Management</h1>
            <TableSelector tables={tables} onSelectTable={setSelectedTable} />
            {selectedTable && (
                <TableServiceProvider service={dataService}>
                    <Table properties={tableProperties} data={rows} />
                </TableServiceProvider>
            )}
        </div>
    );
};

export default DataManagement;
