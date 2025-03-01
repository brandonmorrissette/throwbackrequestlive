import React, {
    createContext,
    ReactNode,
    useContext,
    useEffect,
    useState,
} from 'react';

/**
 * @typedef {Object} AuthContextType
 * @property {string | null} token - The authentication token.
 * @property {string[]} userGroups - The user groups.
 * @property {(token: string) => void} setToken - Function to set the authentication token.
 * @property {(groups: string[]) => void} setUserGroups - Function to set the user groups.
 * @property {() => void} logout - Function to log out the user.
 */
interface AuthContextType {
    token: string | null;
    userGroups: string[];
    setToken: (token: string) => void;
    setUserGroups: (groups: string[]) => void;
    logout: () => void;
}

/**
 * Context to handle authentication state.
 * @type {React.Context<AuthContextType | undefined>}
 */
const AuthContext = createContext<AuthContextType | undefined>(undefined);

/**
 * Custom hook to use the AuthContext.
 * @throws Will throw an error if used outside of AuthProvider.
 * @returns {AuthContextType} The auth context value.
 */
export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

/**
 * @typedef {Object} AuthProviderProps
 * @property {ReactNode} children - Child components.
 */
interface AuthProviderProps {
    children: ReactNode;
}

/**
 * AuthProvider component to wrap around components that need access to auth context.
 * @param {AuthProviderProps} props - Component props.
 * @returns {JSX.Element} The provider component.
 */
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
