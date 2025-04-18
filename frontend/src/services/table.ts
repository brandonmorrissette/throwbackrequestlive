import { parse } from 'papaparse';
import { Row } from '../components/table/Row';

export class TableService {
    constructor(private tableService: any) {}

    /**
     * Adds a new row to the table.
     * @param {any} gridApi - The grid API instance.
     * @param {Row[]} rowData - The current row data.
     * @returns {Row[]} The updated row data.
     */
    addRow(gridApi: any, rowData: Row[]): Row[] {
        const newRow: Row = {} as Row;
        gridApi.applyTransaction({ add: [newRow] });
        return [...rowData, newRow];
    }

    /**
     * Deletes selected rows from the table.
     * @param {any} gridApi - The grid API instance.
     * @param {Row[]} selectedRows - The rows to be deleted.
     * @param {Row[]} rowData - The current row data.
     * @returns {Row[]} The updated row data.
     */
    deleteRow(gridApi: any, selectedRows: Row[], rowData: Row[]): Row[] {
        gridApi.applyTransaction({ remove: selectedRows });
        return rowData.filter((row) => !selectedRows.includes(row));
    }

    /**
     * Saves changes to the table.
     * @param {string} table_name - The name of the table.
     * @param {string} token - The authentication token.
     * @param {Row[]} rowData - The current row data.
     * @returns {Promise<any[]>} The updated row data from the server.
     */
    async saveChanges(
        table_name: string,
        token: string | null,
        rowData: Row[]
    ): Promise<any[]> {
        await this.tableService.putRows(table_name, token, rowData);
        return await this.tableService.getRows(table_name, token);
    }

    /**
     * Handles file upload and parses CSV data.
     * @param {File} file - The uploaded file.
     * @param {Row[]} rowData - The current row data.
     * @param {(data: Row[]) => void} setRowData - Function to update row data.
     * @param {(unsaved: boolean) => void} setUnsavedChanges - Function to set unsaved changes flag.
     */
    handleFileUpload(
        file: File,
        rowData: Row[],
        setRowData: (data: Row[]) => void,
        setUnsavedChanges: (unsaved: boolean) => void
    ): void {
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
