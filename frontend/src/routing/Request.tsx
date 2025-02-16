const apiRequest = async (
    url: string,
    options: RequestInit = {}
): Promise<any> => {
    const token = sessionStorage.getItem('auth_token');
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }
    const response = await fetch(url, { ...options, headers });
    console.log('response:', response);
    await validate(response);
    return response.json();
};

export default apiRequest;

async function validate(response: Response) {
    if (!response.ok) {
        console.error('Error in validation:', response);
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            `${response.status} - ${errorData.error || response.statusText}`
        );
    }
}
