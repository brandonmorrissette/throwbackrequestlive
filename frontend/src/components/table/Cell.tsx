import type { ICellEditorComp, ICellEditorParams } from 'ag-grid-community';
import moment from 'moment';
import React from 'react';
import Datetime from 'react-datetime';
import 'react-datetime/css/react-datetime.css';
import ReactDOM from 'react-dom';

const dateFormat = 'YYYY-MM-DD';
const timeFormat = 'HH:mm:ss';

/**
 * Custom cell editor for datetime.
 */
export class DateTimeCellEditor implements ICellEditorComp {
    value: string;
    pickerRef: any;
    eGui: any;

    constructor() {
        this.value = '';
        this.pickerRef = React.createRef();
    }

    /**
     * Initializes the cell editor.
     * @param {ICellEditorParams} params - The cell editor parameters.
     */
    init(params: ICellEditorParams) {
        this.value = params.value
            ? moment.utc(params.value).format(`${dateFormat} ${timeFormat}`)
            : moment.utc().format(`${dateFormat} ${timeFormat}`);
        this.eGui = document.createElement('div');
        this.eGui.className = 'ag-custom-component-popup';
    }

    /**
     * Handles the change event for the date picker.
     * @param {any} date - The selected date.
     */
    onChange = (date: any) => {
        this.value = date.utc().format(`${dateFormat} ${timeFormat}`);
    };

    /**
     * Returns the GUI for the cell editor.
     * @returns {HTMLElement} The GUI element.
     */
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

    /**
     * Called after the GUI is attached to the DOM.
     */
    afterGuiAttached() {
        const input = this.eGui.querySelector('input');
        if (input) {
            input.focus();
            input.click();
        }
    }

    /**
     * Returns the value from the cell editor.
     * @returns {string} The value.
     */
    getValue() {
        return this.value;
    }

    /**
     * Destroys the cell editor.
     */
    destroy() {
        ReactDOM.unmountComponentAtNode(this.eGui);
    }

    /**
     * Indicates if the cell editor is a popup.
     * @returns {boolean} True if the cell editor is a popup.
     */
    isPopup() {
        return true;
    }
}

export default DateTimeCellEditor;
