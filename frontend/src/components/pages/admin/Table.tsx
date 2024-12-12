import React, { useEffect, useState } from 'react';
import apiRequest from '../../routing/Request';

type Column = {
    name: string;
    type: string;
    nullable: boolean;
    foreignKeys: string[];
};

type Row = {
    [key: string]: any;
};

type TableProps = {
    tableName: string;
};

const mapInputType = (dbType: string): string => {
    switch (dbType.toUpperCase()) {
        case 'VARCHAR':
        case 'TEXT':
            return 'text';
        case 'INT':
        case 'INTEGER':
            return 'number';
        case 'DATE':
            return 'date';
        default:
            return 'text';
    }
};

const EditableRow: React.FC<{
    row: Row;
    columns: Column[];
    onSave: () => void;
    onCancel: () => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement>, key: string) => void;
}> = ({ row, columns, onSave, onCancel, onChange }) => (
    <tr>
        {columns.map((col) => (
            <td key={col.name}>
                <input
                    type={mapInputType(col.type)}
                    value={row[col.name] || ''}
                    onChange={(e) => onChange(e, col.name)}
                />
            </td>
        ))}
        <td>
            <button onClick={onSave}>Save</button>
            <button onClick={onCancel}>Cancel</button>
        </td>
    </tr>
);

const ReadOnlyRow: React.FC<{
    row: Row;
    columns: Column[];
    onEdit: () => void;
    onDelete: () => void;
}> = ({ row, columns, onEdit, onDelete }) => (
    <tr>
        {columns.map((col) => (
            <td key={col.name}>{row[col.name]}</td>
        ))}
        <td>
            <button onClick={onEdit}>Edit</button>
            <button onClick={onDelete}>Delete</button>
        </td>
    </tr>
);

const AddRowForm: React.FC<{
    columns: Column[];
    newRow: Row;
    onChange: (e: React.ChangeEvent<HTMLInputElement>, key: string) => void;
    onAdd: () => void;
}> = ({ columns, newRow, onChange, onAdd }) => (
    <tr>
        {columns.map((col) => (
            <td key={col.name}>
                <input
                    type={mapInputType(col.type)}
                    value={newRow[col.name] || ''}
                    onChange={(e) => onChange(e, col.name)}
                />
            </td>
        ))}
        <td>
            <button onClick={onAdd}>Add</button>
        </td>
    </tr>
);

const Table: React.FC<TableProps> = ({ tableName }) => {
    const [columns, setColumns] = useState<Column[]>([]);
    const [rows, setRows] = useState<Row[]>([]);
    const [editingRow, setEditingRow] = useState<number | null>(null);
    const [newRow, setNewRow] = useState<Row>({});

    useEffect(() => {
        fetchColumns();
        fetchRows();
    }, [tableName]);

    const fetchColumns = async () => {
        try {
            const response = await apiRequest(
                `/api/tables/${tableName}/columns`
            );
            const data = await response.json();
            console.log('Fetched column data:', data);
            setColumns(data);
        } catch (error) {
            console.error('Error fetching columns:', error);
        }
    };

    const fetchRows = async () => {
        try {
            const response = await apiRequest(`/api/tables/${tableName}`);
            const data = await response.json();
            setRows(data);
        } catch (error) {
            console.error('Error fetching rows:', error);
        }
    };

    const handleSaveRow = async (row: Row, index: number | null) => {
        try {
            const method = index === null ? 'POST' : 'PUT';
            const url =
                index === null
                    ? `/api/tables/${tableName}`
                    : `/api/tables/${tableName}/${row.id}`;
            const response = await apiRequest(url, {
                method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(row),
            });

            if (response.ok) {
                if (index === null) {
                    setRows([...rows, row]);
                    setNewRow({});
                } else {
                    setRows(rows.map((r, i) => (i === index ? row : r)));
                    setEditingRow(null);
                }
            } else {
                console.error('Error saving row:', await response.json());
            }
        } catch (error) {
            console.error('An unexpected error occurred:', error);
        }
    };

    const handleDeleteRow = async (id: number) => {
        if (!window.confirm('Are you sure you want to delete this row?')) {
            return;
        }

        try {
            const response = await apiRequest(
                `/api/tables/${tableName}/${id}`,
                {
                    method: 'DELETE',
                }
            );

            if (response.ok) {
                setRows(rows.filter((row) => row.id !== id));
            } else {
                console.error('Error deleting row:', await response.json());
            }
        } catch (error) {
            console.error('An unexpected error occurred:', error);
        }
    };

    const handleInputChange = (
        e: React.ChangeEvent<HTMLInputElement>,
        row: Row,
        key: string
    ) => {
        const updatedRow = { ...row, [key]: e.target.value };
        if (editingRow === null) {
            setNewRow(updatedRow);
        } else {
            setRows(rows.map((r, i) => (i === editingRow ? updatedRow : r)));
        }
    };

    const validateNewRow = () => {
        for (const col of columns) {
            if (col.type !== 'VARCHAR' && !newRow[col.name]) {
                alert(`Field ${col.name} is required.`);
                return false;
            }
        }
        return true;
    };

    return (
        <div>
            <h1>{tableName} Management</h1>
            <table>
                <thead>
                    <tr>
                        {columns.map((col) => (
                            <th key={col.name}>{col.name}</th>
                        ))}
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
                    {rows.map((row, index) =>
                        editingRow === index ? (
                            <EditableRow
                                key={row.id || index}
                                row={row}
                                columns={columns}
                                onSave={() => handleSaveRow(row, index)}
                                onCancel={() => setEditingRow(null)}
                                onChange={(e, key) =>
                                    handleInputChange(e, row, key)
                                }
                            />
                        ) : (
                            <ReadOnlyRow
                                key={row.id || index}
                                row={row}
                                columns={columns}
                                onEdit={() => setEditingRow(index)}
                                onDelete={() => handleDeleteRow(row.id)}
                            />
                        )
                    )}
                    <AddRowForm
                        columns={columns}
                        newRow={newRow}
                        onChange={(e, key) => handleInputChange(e, newRow, key)}
                        onAdd={() => {
                            if (validateNewRow()) {
                                handleSaveRow(newRow, null);
                            }
                        }}
                    />
                </tbody>
            </table>
        </div>
    );
};

export default Table;
