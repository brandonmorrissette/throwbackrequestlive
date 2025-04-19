import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useError } from '../../contexts/ErrorContext';
import get from '../../routing/Request';

interface PasswordResetProps {
    session: string;
    username: string;
}

/**
 * PasswordReset component that allows users to reset their password.
 * @component
 * @param {PasswordResetProps} props - The properties for the PasswordReset component.
 * @param {string} props.session - The session identifier.
 * @param {string} props.username - The username of the user.
 */
const PasswordReset: React.FC<PasswordResetProps> = ({ session, username }) => {
    const [newPassword, setNewPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const { setError } = useError();

    const navigate = useNavigate();

    const handlePasswordReset = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);

        try {
            const response = await get('/api/login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username,
                    password: newPassword,
                    session,
                    password_reset: true,
                }),
            });

            if (response.success) {
                navigate('/admin');
            } else {
                throw new Error(
                    response.error ||
                        'An unexpected error occurred during password reset.'
                );
            }
        } catch (error: any) {
            setError(error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="content-wrapper">
            <h2 className="text-center">Set New Password</h2>
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
