import React from 'react';

/**
 * Props for the TableSelector component.
 * @property {string[]} tables - The list of table names to select from.
 * @property {(tableName: string) => void} onSelectTable - Function to call when a table is selected.
 */
type TableSelectorProps = {
    tables: string[];
    onSelectTable: (tableName: string) => void;
};

/**
 * A functional component that renders a dropdown to select a table.
 * @param {TableSelectorProps} props - The props for the component.
 * @returns {JSX.Element} The rendered component.
 */
const TableSelector: React.FC<TableSelectorProps> = ({
    tables,
    onSelectTable,
}) => {
    return (
        <div>
            <label htmlFor="table-selector">Select Table </label>
            <select
                id="table-selector"
                onChange={(e) => onSelectTable(e.target.value)}
            >
                <option value="">--Select a table--</option>
                {tables.map((table) => (
                    <option key={table} value={table}>
                        {table}
                    </option>
                ))}
            </select>
        </div>
    );
};

export default TableSelector;
