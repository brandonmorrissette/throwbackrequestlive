import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../context/AuthContext';
import PasswordReset from './PasswordReset';

const LoginForm: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showPasswordReset, setShowPasswordReset] = useState(false);
    const [session, setSession] = useState('');

    const { setToken } = useAuth();
    const navigate = useNavigate();

    const handleLogin = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const response = await fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password }),
        });

        const data = await response.json();

        if (response.ok && data.success) {
            sessionStorage.setItem('auth_token', data.token);
            setToken(data.token);
            navigate('/admin');
        } else if (data.error === 'New password required') {
            setSession(data.session);
            setShowPasswordReset(true);
        } else {
            setError('Invalid login credentials.');
        }
    };

    if (showPasswordReset) {
        return <PasswordReset session={session} username={username} />;
    }

    return (
        <div className="content-wrapper">
            <h2 className="text-center">Login</h2>
            {error && <p className="error-message">{error}</p>}
            <form onSubmit={handleLogin} className="contact-form">
                <div className="form-group">
                    <label htmlFor="username">Username:</label>
                    <input
                        type="text"
                        id="username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="password">Password:</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group text-center">
                    <button type="submit" disabled={loading}>
                        {loading ? 'Logging in...' : 'Login'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default LoginForm;
