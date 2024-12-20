import React, { ReactNode } from 'react';
import {
    Route,
    BrowserRouter as Router,
    Routes,
    useLocation,
} from 'react-router-dom';
import Content from './components/app/content/Content';
import Footer from './components/app/footer/Footer';
import Header from './components/app/header/Header';
import ProtectedRoute from './components/routing/ProtectedRoute';
import { AuthProvider } from './context/AuthContext';
import Admin from './pages/Admin';
import Home from './pages/Home';
import Login from './pages/Login';
import Vote from './pages/Vote';

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
