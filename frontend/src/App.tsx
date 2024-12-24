import React, { ReactNode } from 'react';
import {
    Route,
    BrowserRouter as Router,
    Routes,
    useLocation,
} from 'react-router-dom';
import Content from './components/content/Content';
import Footer from './components/footer/Footer';
import Header from './components/header/Header';
import { AuthProvider } from './contexts/AuthContext';
import Admin from './pages/admin/Admin';
import Home from './pages/home/Home';
import Login from './pages/login/Login';
import Vote from './pages/request/Vote';
import ProtectedRoute from './routing/ProtectedRoute';

const App: React.FC = () => {
    return (
        <AuthProvider>
            <Router>
                <div>
                    <Header />
                    <ContentWrapper>
                        <Routes>
                            <Route path="/" element={<Home />} />
                            <Route path="/vote" element={<Vote />} />
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
                </div>
            </Router>
        </AuthProvider>
    );
};

// The admin area is not expected to be mobile, hence the wider content.
// The following code is exclusively for that
interface ContentWrapperProps {
    children: ReactNode;
}

const ContentWrapper: React.FC<ContentWrapperProps> = ({ children }) => {
    const location = useLocation();
    const isAdminRoute = location.pathname === '/admin';
    const containerClass = isAdminRoute ? 'wide-content' : 'content';

    return <Content className={containerClass}>{children}</Content>;
};

export default App;
