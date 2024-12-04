import React, { useEffect, useState } from 'react';
import Select from 'react-select';
import { Tab, TabList, TabPanel, Tabs } from 'react-tabs';
import 'react-tabs/style/react-tabs.css';
import apiRequest from '../../routing/Request';
import Table from './Table';

type TableMetadata = {
    name: string;
    recordCount: number;
    lastUpdated: string;
};

const DataManagement: React.FC = () => {
    const [tables, setTables] = useState<TableMetadata[]>([]);
    const [openTables, setOpenTables] = useState<TableMetadata[]>([]);
    const [activeTabIndex, setActiveTabIndex] = useState<number>(0);

    useEffect(() => {
        fetchTables();
    }, []);

    const fetchTables = async () => {
        try {
            const response = await apiRequest('/api/tables');
            const data = await response.json();
            setTables(data);
        } catch (error) {
            console.error('Error fetching tables:', error);
        }
    };

    const handleTableClick = (table: TableMetadata) => {
        const existingIndex = openTables.findIndex(
            (t) => t.name === table.name
        );
        if (existingIndex === -1) {
            setOpenTables([...openTables, table]);
            setActiveTabIndex(openTables.length);
        } else {
            setActiveTabIndex(existingIndex);
        }
    };

    const handleTabClose = (index: number) => {
        const newOpenTables = openTables.filter((_, i) => i !== index);
        setOpenTables(newOpenTables);
        if (index === activeTabIndex) {
            setActiveTabIndex(Math.max(0, index - 1));
        } else if (index < activeTabIndex) {
            setActiveTabIndex(activeTabIndex - 1);
        }
    };

    const handleSelectChange = (selectedOption: any) => {
        if (selectedOption) {
            handleTableClick(selectedOption.value);
        }
    };

    return (
        <div>
            <h1>Data Management</h1>
            <Select
                options={tables.map((table) => ({
                    value: table,
                    label: `${table.name} (${table.recordCount})`,
                }))}
                placeholder="Search tables..."
                onChange={handleSelectChange}
            />
            <Tabs
                selectedIndex={activeTabIndex}
                onSelect={(index: number) => setActiveTabIndex(index)} // Explicitly type 'index'
            >
                <TabList>
                    {openTables.map((table, index) => (
                        <Tab key={table.name} className="tab">
                            {table.name}
                            <span className="badge">{table.recordCount}</span>
                            <button
                                className="close-button"
                                onClick={() => handleTabClose(index)}
                            >
                                x
                            </button>
                        </Tab>
                    ))}
                </TabList>
                {openTables.map((table) => (
                    <TabPanel key={table.name}>
                        <Table tableName={table.name} />
                    </TabPanel>
                ))}
            </Tabs>
        </div>
    );
};

export default DataManagement;
