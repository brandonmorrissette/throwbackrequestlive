import { parse } from 'papaparse';
import { Options } from '../components/table/Options';
import { Row } from '../components/table/Row';

export class TableService {
    constructor(private tableService: any) {}

    addRow(gridApi: any, rowData: Row[]) {
        const newRow: Row = {} as Row;
        gridApi.applyTransaction({ add: [newRow] });
        return [...rowData, newRow];
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
        rowData: Row[],
        setRowData: (data: Row[]) => void,
        setUnsavedChanges: (unsaved: boolean) => void
    ) {
        parse(file, {
            header: true,
            complete: (results: { data: any }) => {
                setRowData([...rowData, ...results.data]);
                setUnsavedChanges(true);
            },
            error: (error: unknown) => {
                console.error('Error parsing CSV file:', error);
            },
        });
    }
}
