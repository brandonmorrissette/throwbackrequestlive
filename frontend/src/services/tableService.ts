export interface TableService {
    getTableProperties(tableName: string): Promise<any>;
    readRows(tableName: string): Promise<any[]>;
    writeRows(tableName: string, rows: any[]): Promise<void>;
}
