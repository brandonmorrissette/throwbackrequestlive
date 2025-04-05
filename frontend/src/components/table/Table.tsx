import {
    AllCommunityModule,
    GridReadyEvent,
    ModuleRegistry,
    RowSelectionOptions,
} from 'ag-grid-community';
import { AgGridReact } from 'ag-grid-react';
import React, { useEffect, useMemo, useState } from 'react';
import { useError } from '../../contexts/ErrorContext';
import { useServices } from '../../contexts/TableServiceContext';
import { TableService } from '../../services/table';
import { Options } from './Options';
import { Row } from './Row';

ModuleRegistry.registerModules([AllCommunityModule]);

/**
 * Table component to display and manage data in a grid.
 * @param {Object} props - The props for the component.
 * @param {Row[]} props.data - The data to be displayed in the table.
 * @param {Options} props.options - The configuration options for the table.
 * @returns {JSX.Element} The rendered component.
 */
const Table: React.FC<{
    data: Row[];
    options: Options;
}> = ({ data, options: init }) => {
    const { tableService } = useServices();
    const [rowData, setRowData] = useState<Row[]>(data);
    const [options, setOptions] = useState<Options>(init);
    const [gridApi, setGridApi] = useState<any>(null);
    const [selectedRows, setSelectedRows] = useState<Row[]>([]);
    const [unsavedChanges, setUnsavedChanges] = useState(false);
    const { setError } = useError();

    const tableServiceInstance = useMemo(
        () => new TableService(tableService),
        [tableService]
    );

    useEffect(() => {
        setRowData(data);
    }, [data]);

    useEffect(() => {
        setOptions(init);
    }, [init]);

    useEffect(() => {
        return () => {
            gridApi?.removeEventListener('rowSelected', onRowSelected);
        };
    }, [gridApi]);

    /**
     * Handles the grid ready event.
     * @param {GridReadyEvent} params - The grid ready event parameters.
     */
    const onGridReady = (params: GridReadyEvent) => {
        setGridApi(params.api);
        params.api.addEventListener('rowSelected', onRowSelected);
    };

    /**
     * Handles the row selected event.
     * @param {any} event - The row selected event.
     */
    const onRowSelected = (event: any) => {
        const selectedNodes = event.api.getSelectedNodes();
        const selectedData = selectedNodes.map((node: any) => node.data);
        setSelectedRows(selectedData);
    };

    /**
     * Handles the cell value changed event.
     * @param {any} event - The cell value changed event.
     */
    const onCellValueChanged = (event: any) => {
        const updatedRowData = rowData.map((row) => {
            if (row.id === event.data.id) {
                return { ...row, [event.colDef.field]: event.newValue };
            }
            return row;
        });
        setRowData(updatedRowData);
        setUnsavedChanges(true);
    };

    /**
     * Adds a new row to the table.
     */
    const addRow = () => {
        if (gridApi) {
            const updatedRowData = tableServiceInstance.addRow(
                gridApi,
                rowData
            );
            setRowData(updatedRowData);
            setUnsavedChanges(true);
        }
    };

    /**
     * Deletes the selected rows from the table.
     */
    const deleteRow = () => {
        if (gridApi && selectedRows.length > 0) {
            const updatedRowData = tableServiceInstance.deleteRow(
                gridApi,
                selectedRows,
                rowData
            );
            setRowData(updatedRowData);
            setSelectedRows([]);
            setUnsavedChanges(true);
        }
    };

    /**
     * Saves the changes made to the table.
     */
    const saveChanges = async () => {
        try {
            console.log('Rows to save:', rowData);
            const updatedRows = await tableServiceInstance.saveChanges(
                options,
                rowData
            );
            setRowData(updatedRows);
            setUnsavedChanges(false);
        } catch (error: any) {
            setError(error);
            console.error('Error saving changes:', error);
        }
    };

    /**
     * Handles the file upload event.
     * @param {React.ChangeEvent<HTMLInputElement>} event - The file upload event.
     */
    const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (file) {
            tableServiceInstance.handleFileUpload(
                file,
                rowData,
                setRowData,
                setUnsavedChanges
            );
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
                    height: '60vh',
                    padding: '10px',
                    margin: '0 auto',
                }}
            >
                <AgGridReact
                    rowData={rowData}
                    columnDefs={options.columns}
                    rowSelection={useMemo<
                        RowSelectionOptions | 'single' | 'multiple'
                    >(() => {
                        return {
                            mode: 'multiRow',
                        };
                    }, [])}
                    onGridReady={onGridReady}
                    onCellValueChanged={onCellValueChanged}
                    rowClassRules={{
                        'selected-row': (params: any) =>
                            params.node.isSelected(),
                    }}
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
