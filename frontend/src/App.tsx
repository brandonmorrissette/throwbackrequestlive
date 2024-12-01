import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
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
                    <Content>
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
                    </Content>
                    <Footer />
                </div>
            </Router>
        </AuthProvider>
    );
};

export default App;
