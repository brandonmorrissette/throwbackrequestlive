import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useError } from '../../contexts/ErrorContext';
import apiRequest from '../../routing/Request';
import PasswordReset from './PasswordReset';

const LoginForm: React.FC = () => {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [showPasswordReset, setShowPasswordReset] = useState(false);
    const [session, setSession] = useState('');
    const { setError } = useError();

    const { setToken } = useAuth();
    const navigate = useNavigate();

    const login = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await apiRequest('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password }),
            });

            if (response.error === 'NEW_PASSWORD_REQUIRED') {
                console.log('Password reset required:', response);
                setSession(response.session);
                setShowPasswordReset(true);
            } else if (response.success) {
                console.log('Login successful:', response);
                sessionStorage.setItem('auth_token', response.token);
                setToken(response.token);
                navigate('/admin');
            } else {
                throw new Error(
                    response.error ||
                        'An unexpected error occurred during login.'
                );
            }
        } catch (error: any) {
            setPassword('');
            setLoading(false);
            setError(error);
            console.error('Error logging in:', error);
        }
    };

    if (showPasswordReset) {
        return <PasswordReset session={session} username={username} />;
    }

    return (
        <div className="content-wrapper">
            <h2 className="text-center">Login</h2>
            <form onSubmit={login} className="contact-form">
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
