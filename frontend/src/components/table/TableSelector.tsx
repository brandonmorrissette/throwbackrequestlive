import React from 'react';

type TableSelectorProps = {
    tables: string[];
    onSelectTable: (tableName: string) => void;
};

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
