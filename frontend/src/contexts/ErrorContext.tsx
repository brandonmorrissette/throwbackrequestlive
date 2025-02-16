import React, {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react';
import { toast } from 'react-toastify';

interface ErrorContextType {
    setError: (error: Error) => void;
}

const ErrorContext = createContext<ErrorContextType | undefined>(undefined);

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

export const useError = (): ErrorContextType => {
    const context = useContext(ErrorContext);
    if (!context)
        throw new Error('useError must be used within an ErrorProvider');
    return context;
};
