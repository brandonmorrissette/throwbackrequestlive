import { ColDef as BaseColDef, ICellEditorComp } from 'ag-grid-community';
import { DateTimeCellEditor } from './Cell';

export class ColDef implements BaseColDef {
    field: string = '';
    headerName: string = '';
    autoIncrement?: boolean = false;
    editable?: boolean = !this.autoIncrement;
    sortable?: boolean = true;
    cellDataType?: string = 'text';
    cellEditor?: new () => ICellEditorComp;
    cellEditorPopup?: boolean = false;
    valueFormatter?: (params: any) => string;
    valueParser?: (params: any) => any = (params) => {
        return params.newValue;
    };

    constructor(init: Partial<ColDef>) {
        Object.assign(this, init);

        if (init.cellDataType == 'date') {
            this.valueFormatter = (params: any) => {
                const date = new Date(params.value);
                return date.toLocaleDateString();
            };
        }
        if (init.cellDataType === 'datetime') {
            this.cellEditor = DateTimeCellEditor;
            this.cellEditorPopup = true;
            this.valueFormatter = (params: any) => {
                const date = new Date(params.value);
                return date.toLocaleString();
            };
            this.valueParser = (params: any) => {
                console.log('valueParser::params', params);
                const parsedDate = new Date(params.newValue);
                console.log('valueParser::parsedDate', parsedDate);
                return isNaN(parsedDate.getTime())
                    ? params.oldValue
                    : parsedDate.toISOString();
            };
        }
    }
}
