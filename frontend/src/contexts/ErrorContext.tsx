import React, {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react';
import { toast } from 'react-toastify';

/**
 * @typedef {Object} ErrorContextType
 * @property {(error: Error) => void} setError - Function to set the error state.
 */
interface ErrorContextType {
    setError: (error: Error) => void;
}

/**
 * Context to handle global error state.
 * @type {React.Context<ErrorContextType | undefined>}
 */
const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

/**
 * ErrorProvider component to wrap around components that need access to error context.
 * @param {Object} props - Component props.
 * @param {ReactNode} props.children - Child components.
 * @returns {JSX.Element} The provider component.
 */
export const ErrorProvider: React.FC<{ children: ReactNode }> = ({
    children,
}) => {
    const [error, setError] = useState<Error | null>(null);

    useEffect(() => {
        if (error) {
            console.error('Global Error:', error);
            toast.error(
                `Looks like something, somewhere is unhappy\n${error.message}.\nWe're on it.`
            );
            setError(null);
        }
    }, [error]);

    return (
        <ErrorContext.Provider value={{ setError }}>
            {children}
        </ErrorContext.Provider>
    );
};

/**
 * Custom hook to use the ErrorContext.
 * @throws Will throw an error if used outside of ErrorProvider.
 * @returns {ErrorContextType} The error context value.
 */
export const useError = (): ErrorContextType => {
    const context = useContext(ErrorContext);
    if (!context)
        throw new Error('useError must be used within an ErrorProvider');
    return context;
};
