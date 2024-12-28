import {
    AllCommunityModule,
    ColDef as BaseColDef,
    GridReadyEvent,
    ModuleRegistry,
    RowSelectionOptions,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import { parse } from 'papaparse';
import React, { useEffect, useMemo, useState } from 'react';
import { useServices } from '../../contexts/TableServiceContext';

ModuleRegistry.registerModules([AllCommunityModule]);

export class ColDef implements BaseColDef {
    field: string = '';
    headerName: string = '';
    editable?: boolean = false;
    sortable?: boolean = false;
    valueFormatter?: (params: any) => string;
    cellDataType?: string;

    constructor(init: Partial<ColDef>) {
        Object.assign(this, init);
    }
}

interface RowData {
    [key: string]: any;
}

export class Properties {
    name: string;
    columns: ColDef[];
    primaryKeys: ColDef[];

    constructor(
        name: string,
        columns: ColDef[],
        primaryKeys?: ColDef[],
        ...additionalProps: any[]
    ) {
        this.name = name;
        this.columns = columns;
        this.primaryKeys = primaryKeys || [];

        additionalProps.forEach((prop) => {
            Object.entries(prop).forEach(([key, value]) => {
                if (!(key in this)) {
                    (this as any)[key] = value;
                } else {
                    console.log('Property already exists:', key);
                }
            });
        });
    }
}

type TableProps = {
    data: RowData[];
    properties: Properties;
};

const Table: React.FC<TableProps> = ({ data, properties }) => {
    const { tableService } = useServices();
    const [rowData, setRowData] = useState<RowData[]>(data);
    const [tableProperties, setProperties] = useState<Properties>(properties);
    const [gridApi, setGridApi] = useState<any>(null);
    const [selectedRows, setSelectedRows] = useState<RowData[]>([]);
    const [unsavedChanges, setUnsavedChanges] = useState(false);

    useEffect(() => {
        console.log('Table::useEffect', data);
        setRowData(data);
    }, [data]);

    useEffect(() => {
        setProperties(properties);
    }, [properties]);

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
        const updatedRowData = rowData.map((row) => {
            const isPrimaryKeyMatch = tableProperties.primaryKeys.every(
                (key) => row[key.field] === event.data[key.field]
            );
            return isPrimaryKeyMatch ? event.data : row;
        });
        setRowData(updatedRowData);
        setUnsavedChanges(true);
    };

    const addRow = () => {
        if (gridApi) {
            const newRow: RowData = {} as RowData;
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
            await tableService.writeRows(tableProperties.name, rowData);
            const updatedRows = await tableService.readRows(
                tableProperties.name
            );
            setRowData(updatedRows);
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

    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            parse(file, {
                header: true,
                complete: (results: { data: any }) => {
                    const data = results.data as RowData[];
                    setRowData((prevRowData) => [...prevRowData, ...data]);
                },
                error: (error: unknown) => {
                    console.error('Error parsing CSV file:', error);
                },
            });
        }
    };

    return (
        <div>
            <div>
                <h2>Upload CSV</h2>
                <input type="file" accept=".csv" onChange={handleFileUpload} />
            </div>
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
                    columnDefs={tableProperties.columns}
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
