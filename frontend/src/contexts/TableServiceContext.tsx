import React, { createContext, ReactNode, useContext } from 'react';
import { TableService } from '../services/tableService';

interface ServiceContextProps {
    tableService: TableService;
}

const ServiceContext = createContext<ServiceContextProps | undefined>(
    undefined
);

export const TableServiceProvider: React.FC<{
    children: ReactNode;
    service: TableService;
}> = ({ children, service }) => {
    return (
        <ServiceContext.Provider value={{ tableService: service }}>
            {children}
        </ServiceContext.Provider>
    );
};

export const useServices = (): ServiceContextProps => {
    const context = useContext(ServiceContext);
    if (!context) {
        throw new Error('useServices must be used within a ServiceProvider');
    }
    return context;
};
