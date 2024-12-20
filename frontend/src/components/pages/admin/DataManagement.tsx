import React, { useEffect, useState } from 'react';
import { getColumns, getRows, getTableNames } from '../../../services/data';
import Table from './Table';
import TableSelector from './TableSelector';

const DataManagement: React.FC = () => {
    const [tables, setTables] = useState<string[]>([]);
    const [selectedTable, setSelectedTable] = useState<string | null>(null);
    const [tableData, setTableData] = useState<any[]>([]);
    const [columnDefs, setColumnDefs] = useState<any[]>([]);

    useEffect(() => {
        fetchTableNames();
    }, []);

    useEffect(() => {
        if (selectedTable) {
            fetchTableData(selectedTable);
            fetchColumnDefs(selectedTable);
        }
    }, [selectedTable]);

    const fetchTableNames = async () => {
        try {
            const data = await getTableNames();
            setTables(data);
        } catch (error) {
            console.error('Error fetching table names:', error);
        }
    };

    const fetchTableData = async (tableName: string) => {
        try {
            const data = await getRows(tableName);
            setTableData(data);
        } catch (error) {
            console.error('Error fetching table data:', error);
        }
    };

    const fetchColumnDefs = async (tableName: string) => {
        try {
            const columns = await getColumns(tableName);
            setColumnDefs(
                columns.map((col: any) => ({ headerName: col.name }))
            );
        } catch (error) {
            console.error('Error fetching column definitions:', error);
        }
    };

    return (
        <div>
            <h1>Data Management</h1>
            <TableSelector tables={tables} onSelectTable={setSelectedTable} />
            {selectedTable && (
                <Table
                    table_name={selectedTable}
                    data={tableData}
                    columns={columnDefs}
                />
            )}
        </div>
    );
};

export default DataManagement;
