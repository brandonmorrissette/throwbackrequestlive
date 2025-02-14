import { toast } from 'react-toastify';

const apiRequest = async (
    url: string,
    options: RequestInit = {}
): Promise<any> => {
    const token = sessionStorage.getItem('auth_token');
    const headers = new Headers(options.headers || {});
    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    try {
        const response = await fetch(url, { ...options, headers });
        await validate(response);
        return response.json();
    } catch (error) {
        console.error('API Request Failed:', error);
        handleError(error as RequestError);
    }
};

export default apiRequest;

class RequestError extends Error {
    status: number;

    constructor(message?: string, status?: number) {
        super(message);
        this.status = status || 500;
        this.name = 'RequestError';
    }
}

async function handleError(error: RequestError) {
    if (error.status === 401) {
        redirectUnauthorizedUser();
    } else {
        toast.warn(
            `Looks like something, somewhere isn't happy.\nError Code ${error.status}\n${error.message}\n`
        );
    }

    throw error;
}

async function validate(response: Response) {
    if (!response.ok) {
        console.error('Error in validation:', response);
        const errorData = await response.json().catch(() => ({}));
        throw new RequestError(
            errorData.error || response.statusText,
            response.status
        );
    }
}

function redirectUnauthorizedUser() {
    sessionStorage.removeItem('auth_token');
    window.location.href = '/login';
}
