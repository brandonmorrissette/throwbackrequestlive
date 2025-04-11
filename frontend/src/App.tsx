import 'bootstrap/dist/css/bootstrap.min.css';
import 'bootstrap/dist/js/bootstrap.bundle.min.js';

import React from 'react';
import {
    Navigate,
    Route,
    BrowserRouter as Router,
    Routes,
} from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Content from './components/content/Content';
import Footer from './components/footer/Footer';
import Header from './components/header/Header';
import { AuthProvider } from './contexts/AuthContext';
import { ErrorProvider } from './contexts/ErrorContext';
import DataManagement from './pages/data/DataManagement';
import Home from './pages/home/Home';
import Login from './pages/login/Login';
import Request from './pages/request/Request';
import ShowManagement from './pages/shows/ShowManagement';
import UserManagement from './pages/users/UserManagement';
import ProtectedRoute from './routing/ProtectedRoute';

/**
 * The main application component that sets up the routing and context providers.
 * @returns {React.FC} The App component.
 */
const App: React.FC = () => {
    return (
        <AuthProvider>
            <ErrorProvider>
                <Router>
                    <div>
                        <Header />
                        <Content>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/request" element={<Request />} />
                                <Route path="/login" element={<Login />} />
                                <Route
                                    path="/shows"
                                    element={
                                        <ProtectedRoute redirectTo="/login">
                                            <ShowManagement />
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/data"
                                    element={
                                        <ProtectedRoute redirectTo="/login">
                                            <DataManagement />
                                        </ProtectedRoute>
                                    }
                                />
                                <Route
                                    path="/users"
                                    element={
                                        <ProtectedRoute redirectTo="/login">
                                            <UserManagement />
                                        </ProtectedRoute>
                                    }
                                />
                                <Route path="*" element={<Navigate to="/" />} />
                            </Routes>
                        </Content>
                        <Footer />
                        <ToastContainer
                            position="top-center"
                            autoClose={10000}
                        />
                    </div>
                </Router>
            </ErrorProvider>
        </AuthProvider>
    );
};

export default App;
