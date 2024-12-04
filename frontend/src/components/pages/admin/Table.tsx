import React, { useEffect, useState } from 'react';
import apiRequest from '../../routing/Request';

type Column = {
    name: string;
    type: string;
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
    schema: Column[];
    onSave: () => void;
    onCancel: () => void;
    onChange: (e: React.ChangeEvent<HTMLInputElement>, key: string) => void;
}> = ({ row, schema, onSave, onCancel, onChange }) => (
    <tr>
        {schema.map((col) => (
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
    schema: Column[];
    onEdit: () => void;
    onDelete: () => void;
}> = ({ row, schema, onEdit, onDelete }) => (
    <tr>
        {schema.map((col) => (
            <td key={col.name}>{row[col.name]}</td>
        ))}
        <td>
            <button onClick={onEdit}>Edit</button>
            <button onClick={onDelete}>Delete</button>
        </td>
    </tr>
);

const AddRowForm: React.FC<{
    schema: Column[];
    newRow: Row;
    onChange: (e: React.ChangeEvent<HTMLInputElement>, key: string) => void;
    onAdd: () => void;
}> = ({ schema, newRow, onChange, onAdd }) => (
    <tr>
        {schema.map((col) => (
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
    const [schema, setSchema] = useState<Column[]>([]);
    const [rows, setRows] = useState<Row[]>([]);
    const [editingRow, setEditingRow] = useState<number | null>(null);
    const [newRow, setNewRow] = useState<Row>({});

    useEffect(() => {
        fetchSchema();
        fetchRows();
    }, [tableName]);

    const fetchSchema = async () => {
        try {
            const response = await apiRequest(
                `/api/tables/${tableName}/schema`
            );
            const data = await response.json();
            setSchema(data);
        } catch (error) {
            console.error('Error fetching schema:', error);
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
        for (const col of schema) {
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
                        {schema.map((col) => (
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
                                schema={schema}
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
                                schema={schema}
                                onEdit={() => setEditingRow(index)}
                                onDelete={() => handleDeleteRow(row.id)}
                            />
                        )
                    )}
                    <AddRowForm
                        schema={schema}
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
