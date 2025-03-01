import React, { createContext, ReactNode, useContext } from 'react';
import { IDataService } from '../services/data';

/**
 * @typedef {Object} ServiceContextProps
 * @property {IDataService} tableService - The table data service.
 */
interface ServiceContextProps {
    tableService: IDataService;
}

/**
 * Context to provide table data service.
 * @type {React.Context<ServiceContextProps | undefined>}
 */
const ServiceContext = createContext<ServiceContextProps | undefined>(
    undefined
);

/**
 * TableServiceProvider component to wrap around components that need access to table service context.
 * @param {Object} props - Component props.
 * @param {ReactNode} props.children - Child components.
 * @param {IDataService} props.service - The table data service.
 * @returns {JSX.Element} The provider component.
 */
export const TableServiceProvider: React.FC<{
    children: ReactNode;
    service: IDataService;
}> = ({ children, service }) => {
    return (
        <ServiceContext.Provider value={{ tableService: service }}>
            {children}
        </ServiceContext.Provider>
    );
};

/**
 * Custom hook to use the ServiceContext.
 * @throws Will throw an error if used outside of TableServiceProvider.
 * @returns {ServiceContextProps} The service context value.
 */
export const useServices = (): ServiceContextProps => {
    const context = useContext(ServiceContext);
    if (!context) {
        throw new Error('useServices must be used within a ServiceProvider');
    }
    return context;
};
