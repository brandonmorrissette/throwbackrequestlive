/**
 * Makes an API request with the given URL and options.
 * Adds an Authorization header if an auth token is present in session storage.
 * Validates the response and returns the parsed JSON data.
 *
 * @param {string} url - The URL to fetch.
 * @param {RequestInit} [options={}] - The options for the fetch request.
 * @returns {Promise<any>} - The parsed JSON response.
 * @throws {Error} - Throws an error if the response is not ok.
 */
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

/**
 * Validates the fetch response.
 * Logs an error and throws an error with the response status and error message if the response is not ok.
 *
 * @param {Response} response - The fetch response to validate.
 * @returns {Promise<void>} - Resolves if the response is ok.
 * @throws {Error} - Throws an error if the response is not ok.
 */
async function validate(response: Response) {
    if (!response.ok) {
        console.error('Error in validation:', response);
        const errorData = await response.json().catch(() => ({}));
        throw new Error(
            `${response.status} - ${errorData.error || response.statusText}`
        );
    }
}
