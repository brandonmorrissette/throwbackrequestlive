import type { ICellEditorComp, ICellEditorParams } from 'ag-grid-community';
import moment from 'moment';
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
        this.value = params.value
            ? moment.utc(params.value).format(`${dateFormat} ${timeFormat}`)
            : moment.utc().format(`${dateFormat} ${timeFormat}`);
        this.eGui = document.createElement('div');
        this.eGui.className = 'ag-custom-component-popup';
    }

    onChange = (date: any) => {
        this.value = date.utc().format(`${dateFormat} ${timeFormat}`);
    };

    getGui(): HTMLElement {
        ReactDOM.render(
            <Datetime
                ref={this.pickerRef}
                value={moment.utc(this.value)}
                onChange={this.onChange}
                dateFormat={dateFormat}
                timeFormat={timeFormat}
                utc={true}
            />,
            this.eGui
        );
        return this.eGui;
    }

    afterGuiAttached() {
        const input = this.eGui.querySelector('input');
        if (input) {
            input.focus();
            input.click();
        }
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
