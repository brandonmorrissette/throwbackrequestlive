import apiRequest from '../components/routing/Request';

export const fetchUsers = async () => {
    const response = await apiRequest('/api/users');
    return response.json();
};

export const fetchGroups = async () => {
    const response = await apiRequest('/api/groups');
    return response.json();
};

export const addUser = async (
    email: string,
    username: string,
    groups: string[]
) => {
    const response = await apiRequest('/api/users', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, username, groups }),
    });
    return response;
};

export const deleteUser = async (username: string) => {
    const response = await apiRequest(`/api/users/${username}`, {
        method: 'DELETE',
    });
    return response;
};

export const updateUser = async (
    username: string,
    email: string,
    groups: string[]
) => {
    const response = await apiRequest(`/api/users/${username}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, groups }),
    });
    return response;
};
