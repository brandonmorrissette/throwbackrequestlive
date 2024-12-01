// src/pages/UserManagement.tsx
import React, { useState } from 'react';

const UserManagement: React.FC = () => {
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    // Submit handler for creating a new user
    const handleCreateUser = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await fetch('/api/cognito/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email }), // Send data for the new user
            });

            const data = await response.json();
            if (data.success) {
                alert('User created successfully!');
            } else {
                setError('Error creating user');
            }
        } catch (err) {
            setError('An error occurred while creating the user');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="content-wrapper">
            <h2 className="text-center">User Management</h2>
            {error && <p className="error-message">{error}</p>}
            <form onSubmit={handleCreateUser} className="contact-form">
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
                    <label htmlFor="email">Email:</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group text-center">
                    <button type="submit" disabled={loading}>
                        {loading ? 'Creating user...' : 'Create User'}
                    </button>
                </div>
            </form>
        </div>
    );
};

export default UserManagement;
