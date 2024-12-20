import {
    AllCommunityModule,
    GridReadyEvent,
    ModuleRegistry,
    RowSelectionOptions,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import React, { useEffect, useMemo, useState } from 'react';
import { writeRows } from '../../../services/data';

ModuleRegistry.registerModules([AllCommunityModule]);

interface RowData {
    [key: string]: any;
}

interface ColumnDef {
    field: string;
    headerName: string;
    editable?: boolean;
    filter?: boolean;
    [key: string]: any;
}

type TableProps = {
    data: RowData[];
    columns: ColumnDef[];
    table_name: string;
};

const Table: React.FC<TableProps> = ({ data, columns, table_name }) => {
    const [rowData, setRowData] = useState<RowData[]>(data);
    const [columnDefs, setColumnDefs] = useState<ColumnDef[]>([]);
    const [gridApi, setGridApi] = useState<any>(null);
    const [selectedRows, setSelectedRows] = useState<RowData[]>([]);
    const [unsavedChanges, setUnsavedChanges] = useState(false);

    useEffect(() => {
        setRowData(data);
    }, [data]);

    useEffect(() => {
        const updatedColumns = columns.map((column) => ({
            ...column,
            editable: true,
            filter: true,
            field: column.field || column.headerName || '',
        }));
        setColumnDefs(updatedColumns);
    }, [columns]);

    useEffect(() => {
        return () => {
            gridApi?.removeEventListener('rowSelected', onRowSelected);
        };
    }, [gridApi]);

    const onGridReady = (params: GridReadyEvent) => {
        setGridApi(params.api);
        params.api.addEventListener('rowSelected', onRowSelected);
    };

    const onRowSelected = (event: any) => {
        const selectedNodes = event.api.getSelectedNodes();
        const selectedData = selectedNodes.map((node: any) => node.data);
        setSelectedRows(selectedData);
    };

    const onCellValueChanged = (event: any) => {
        const updatedRowData = rowData.map((row) =>
            row.id === event.data.id ? event.data : row
        );
        setRowData(updatedRowData);
        setUnsavedChanges(true);
    };

    const addRow = () => {
        if (gridApi) {
            const newRow: RowData = columnDefs.reduce((acc, col) => {
                acc[col.field] = col.field;
                return acc;
            }, {} as RowData);
            gridApi.applyTransaction({ add: [newRow] });
            setRowData((prevRowData) => [...prevRowData, newRow]);
            setUnsavedChanges(true);
        }
    };

    const deleteRow = () => {
        if (gridApi && selectedRows.length > 0) {
            gridApi.applyTransaction({ remove: selectedRows });

            setRowData((prevRowData) =>
                prevRowData.filter((row) => !selectedRows.includes(row))
            );

            setSelectedRows([]);
            setUnsavedChanges(true);
        }
    };

    const saveChanges = async () => {
        try {
            await writeRows(table_name, rowData);
            setUnsavedChanges(false);
        } catch (error) {
            console.error('Error saving changes:', error);
        }
    };

    const rowSelection = useMemo<
        RowSelectionOptions | 'single' | 'multiple'
    >(() => {
        return {
            mode: 'multiRow',
        };
    }, []);

    const rowClassRules = {
        'selected-row': (params: any) => params.node.isSelected(),
    };

    return (
        <div>
            <div
                className="ag-theme-quartz"
                style={{
                    height: 400,
                    padding: '10px',
                    margin: '0 auto',
                }}
            >
                <AgGridReact
                    rowData={rowData}
                    columnDefs={columnDefs}
                    rowSelection={rowSelection}
                    onGridReady={onGridReady}
                    onCellValueChanged={onCellValueChanged}
                    rowClassRules={rowClassRules}
                />
            </div>
            <div className="button-group">
                <button onClick={addRow}>Add Row</button>
                <button
                    onClick={deleteRow}
                    disabled={selectedRows.length === 0}
                >
                    Delete Row
                </button>
                <button onClick={saveChanges} disabled={!unsavedChanges}>
                    Save Changes
                </button>
            </div>
            {unsavedChanges}
        </div>
    );
};

export default Table;
