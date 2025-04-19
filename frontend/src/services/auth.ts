import apiRequest from '../routing/Request';

class AuthService {
    /**
     * Validates the current session by making a request to the /api/validate endpoint.
     * @returns {Promise<any>} The response from the API.
     */
    async validateSession(): Promise<any> {
        const response = await apiRequest('/validate', {
            method: 'GET',
            credentials: 'include',
        });
        return response;
    }
}

export default new AuthService();
