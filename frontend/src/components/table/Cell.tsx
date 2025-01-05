import type { ICellEditorComp, ICellEditorParams } from 'ag-grid-community';
import React from 'react';
import Datetime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import ReactDOM from 'react-dom';

const dateFormat = 'YYYY-MM-DD';
const timeFormat = 'HH:mm:ss';

export class DateTimeCellEditor implements ICellEditorComp {
    value: string;
    pickerRef: any;
    eGui: any;

    constructor() {
        this.value = '';
        this.pickerRef = React.createRef();
    }

    init(params: ICellEditorParams) {
        this.value = params.value || new Date().toISOString();
        this.eGui = document.createElement('div');
        this.eGui.className = 'ag-custom-component-popup';
    }

    onChange = (date: any) => {
        const formattedValue = date.format(`${dateFormat} ${timeFormat}`);
        this.value = formattedValue;
    };

    getGui(): HTMLElement {
        ReactDOM.render(
            <Datetime
                ref={this.pickerRef}
                value={this.value}
                onChange={this.onChange}
                dateFormat={dateFormat}
                timeFormat={timeFormat}
            />,
            this.eGui
        );
        return this.eGui;
    }

    afterGuiAttached() {
        this.eGui.focus();
    }

    getValue() {
        return this.value;
    }

    destroy() {
        ReactDOM.unmountComponentAtNode(this.eGui);
    }

    isPopup() {
        return true;
    }
}

export default DateTimeCellEditor;
