const apiRequest = async (
    url: string,
    options: RequestInit = {}
): Promise<Response> => {
    const token = sessionStorage.getItem('auth_token');
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    return fetch(url, { ...options, headers });
};

export default apiRequest;
