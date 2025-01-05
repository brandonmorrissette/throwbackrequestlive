import { parse } from 'papaparse';
import { Options } from '../components/table/Options';
import { Row } from '../components/table/Row';

export class TableService {
    private autoIncrementIndex = 1;

    constructor(private tableService: any) {}

    addRow(gridApi: any, tableProperties: Options, rowData: Row[]) {
        const newRow: Row = {} as Row;
        const populatedRow = this.populateAutoIncrementFields(
            { data: [newRow] },
            tableProperties
        )[0];
        gridApi.applyTransaction({ add: [populatedRow] });
        return [...rowData, populatedRow];
    }

    deleteRow(gridApi: any, selectedRows: Row[], rowData: Row[]) {
        gridApi.applyTransaction({ remove: selectedRows });
        return rowData.filter((row) => !selectedRows.includes(row));
    }

    async saveChanges(tableProperties: Options, rowData: Row[]) {
        await this.tableService.writeRows(tableProperties.name, rowData);
        return await this.tableService.readRows(tableProperties.name);
    }

    handleFileUpload(
        file: File,
        tableProperties: Options,
        rowData: Row[],
        setRowData: (data: Row[]) => void,
        setUnsavedChanges: (unsaved: boolean) => void
    ) {
        parse(file, {
            header: true,
            complete: (results: { data: any }) => {
                const updatedData = this.populateAutoIncrementFields(
                    results,
                    tableProperties
                );
                setRowData([...rowData, ...updatedData]);
                setUnsavedChanges(true);
            },
            error: (error: unknown) => {
                console.error('Error parsing CSV file:', error);
            },
        });
    }

    private populateAutoIncrementFields(
        results: { data: any },
        tableProperties: Options
    ) {
        const data = results.data as Row[];
        const updatedData = data.map((row) => {
            const autoIncrementColumns = tableProperties.columns
                .filter((col) => col.autoIncrement)
                .map((col) => col.field);

            autoIncrementColumns.forEach((field) => {
                if (!(field in row)) {
                    row[field] = this.autoIncrementIndex++;
                }
            });
            return row;
        });
        return updatedData;
    }
}
