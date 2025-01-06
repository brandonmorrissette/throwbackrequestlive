import { ColDef as BaseColDef, ICellEditorComp } from 'ag-grid-community';
import moment from 'moment';
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
    cellRenderer?: (params: any) => string;
    valueFormatter?: (params: any) => string;
    valueParser?: (params: any) => any = (params) => {
        return params.newValue;
    };
    comparator?: (valueA: any, valueB: any) => number;

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
                const parsedDate = new Date(params.newValue);
                return isNaN(parsedDate.getTime())
                    ? params.oldValue
                    : parsedDate.toISOString();
            };

            this.cellRenderer = (params: any) => {
                const date = moment.utc(params.value);
                return date.format('YYYY-MM-DD HH:mm:ss');
            };

            this.comparator = (valueA, valueB) => {
                const dateA = new Date(valueA);
                const dateB = new Date(valueB);

                if (isNaN(dateA.getTime())) return 1;
                if (isNaN(dateB.getTime())) return -1;

                return dateA.getTime() - dateB.getTime();
            };
        }
    }
}
