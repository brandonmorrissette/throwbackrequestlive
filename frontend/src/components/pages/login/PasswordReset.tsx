import React, { useState } from 'react';

interface PasswordResetProps {
    session: string;
    username: string;
}

const PasswordReset: React.FC<PasswordResetProps> = ({ session, username }) => {
    const [newPassword, setNewPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handlePasswordReset = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            console.log('Session in PasswordReset: ', session);
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username,
                    password: newPassword,
                    session,
                    password_reset: true,
                }),
            });

            const data = await response.json();
            if (data.success) {
                window.location.href = '/admin';
            } else {
                setError('Failed to reset password. Please try again.');
            }
        } catch (err) {
            setError('An error occurred. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="content-wrapper">
            <h2 className="text-center">Set New Password</h2>
            {error && <p className="error-message">{error}</p>}
            <form onSubmit={handlePasswordReset} className="contact-form">
                <div className="form-group">
                    <label htmlFor="newPassword">New Password:</label>
                    <input
                        type="password"
                        id="newPassword"
                        value={newPassword}
                        onChange={(e) => setNewPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group text-center">
                    <button type="submit" disabled={loading}>
                        {loading ? 'Resetting password...' : 'Set New Password'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default PasswordReset;
