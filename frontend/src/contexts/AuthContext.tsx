import React, {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react';

interface AuthContextType {
    token: string | null;
    userGroups: string[];
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
    const [token, setToken] = useState<string | null>(
        sessionStorage.getItem('authToken')
    );
    const [userGroups, setUserGroups] = useState<string[]>(
        JSON.parse(sessionStorage.getItem('userGroups') || '[]')
    );

    useEffect(() => {
        if (token) {
            sessionStorage.setItem('authToken', token);
        } else {
            sessionStorage.removeItem('authToken');
        }
    }, [token]);

    useEffect(() => {
        if (userGroups.length > 0) {
            sessionStorage.setItem('userGroups', JSON.stringify(userGroups));
        } else {
            sessionStorage.removeItem('userGroups');
        }
    }, [userGroups]);

    const logout = () => {
        setToken(null);
        setUserGroups([]);
        sessionStorage.removeItem('authToken');
        sessionStorage.removeItem('userGroups');
    };

    return (
        <AuthContext.Provider
            value={{
                token,
                userGroups,
                setToken,
                setUserGroups,
                logout,
            }}
        >
            {children}
        </AuthContext.Provider>
    );
};
