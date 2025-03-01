import React, { ReactNode } from 'react';
import {
    Route,
    BrowserRouter as Router,
    Routes,
    useLocation,
} from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Content from './components/content/Content';
import Footer from './components/footer/Footer';
import Header from './components/header/Header';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorProvider } from './contexts/ErrorContext';
import Admin from './pages/admin/Admin';
import Home from './pages/home/Home';
import Login from './pages/login/Login';
import Request from './pages/request/Request';
import ProtectedRoute from './routing/ProtectedRoute';

/**
 * The main application component that sets up the routing and context providers.
 * @returns {React.FC} The App component.
 */
const App: React.FC = () => {
    return (
        <ErrorProvider>
            <AuthProvider>
                <Router>
                    <div>
                        <Header />
                        <ContentWrapper>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/request" element={<Request />} />
                                <Route path="/login" element={<Login />} />
                                <Route
                                    path="/admin"
                                    element={
                                        <ProtectedRoute redirectTo="/login">
                                            <Admin />
                                        </ProtectedRoute>
                                    }
                                />
                            </Routes>
                        </ContentWrapper>
                        <Footer />
                        <ToastContainer
                            position="top-center"
                            autoClose={10000}
                        />
                    </div>
                </Router>
            </AuthProvider>
        </ErrorProvider>
    );
};

// The admin area is not expected to be mobile, hence the wider content.
// The following code is exclusively for that
interface ContentWrapperProps {
    children: ReactNode;
}

/**
 * Props for the ContentWrapper component.
 * @typedef {Object} ContentWrapperProps
 * @property {ReactNode} children - The child components to be wrapped.
 */

/**
 * A wrapper component that adjusts the content width based on the route.
 * @param {ContentWrapperProps} props - The props for the ContentWrapper component.
 * @returns {React.FC} The ContentWrapper component.
 */
const ContentWrapper: React.FC<ContentWrapperProps> = ({ children }) => {
    const location = useLocation();
    const isAdminRoute = location.pathname === '/admin';
    const containerClass = isAdminRoute ? 'wide-content' : 'content';

    return <Content className={containerClass}>{children}</Content>;
};

export default App;
