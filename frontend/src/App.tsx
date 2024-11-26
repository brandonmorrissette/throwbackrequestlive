import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Content from './components/app/content/Content';
import Footer from './components/app/footer/Footer';
import Header from './components/app/header/Header';
import Admin from './pages/Admin';
import Home from './pages/Home';
import Vote from './pages/Vote';

const App: React.FC = () => {
    return (
        <Router>
            <div>
                <Header />
                <Content>
                    <Routes>
                        <Route path="/" element={<Home />} />
                        <Route path="/vote" element={<Vote />} />
                        <Route path="/admin" element={<Admin />} />
                    </Routes>
                </Content>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
