import React from 'react';
import { Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import Content from './components/Content';
import Footer from './components/Footer';
import Header from './components/Header';
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
                    </Routes>
                </Content>
                <Footer />
            </div>
        </Router>
    );
};

export default App;
