import React, {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react';

interface AuthContextType {
    isAuthenticated: boolean;
    token: string | null;
    userGroups: string[];
    setIsAuthenticated: (isAuthenticated: boolean) => void;
    setToken: (token: string) => void;
    setUserGroups: (groups: string[]) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

interface AuthProviderProps {
    children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
    const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
    const [token, setToken] = useState<string | null>(
        localStorage.getItem('authToken')
    ); // Persist token
    const [userGroups, setUserGroups] = useState<string[]>(
        JSON.parse(localStorage.getItem('userGroups') || '[]')
    );

    useEffect(() => {
        if (token) {
            setIsAuthenticated(true);
        } else {
            setIsAuthenticated(false);
        }
    }, [token]);

    const logout = () => {
        setToken(null);
        setUserGroups([]);
        localStorage.removeItem('authToken');
        localStorage.removeItem('userGroups');
    };

    return (
        <AuthContext.Provider
            value={{
                isAuthenticated,
                token,
                userGroups,
                setIsAuthenticated,
                setToken,
                setUserGroups,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
