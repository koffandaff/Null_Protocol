const API_URL = 'http://localhost:8000/api';

class Api {
    static baseUrl = API_URL;

    static async request(endpoint, method = 'GET', body = null) {
        const token = localStorage.getItem('access_token');
        const headers = {
            'Content-Type': 'application/json'
        };

        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }

        const config = {
            method,
            headers
        };

        if (body) {
            config.body = JSON.stringify(body);
        }

        try {
            const response = await fetch(`${API_URL}${endpoint}`, config);

            // Handle Unauthorized (Token Expired)
            if (response.status === 401) {
                // Try refresh logic here (simplified for now: logout)
                if (!endpoint.includes('login')) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    localStorage.removeItem('user');
                    window.location.hash = '/login';
                    return null;
                }
            }

            const data = await response.json();

            if (!response.ok) {
                let errorMessage = data.detail || 'API Request Failed';
                if (typeof errorMessage === 'object') {
                    if (Array.isArray(errorMessage)) {
                        // Handle Pydantic validation errors
                        errorMessage = errorMessage.map(err => err.msg).join(', ');
                    } else {
                        errorMessage = JSON.stringify(errorMessage);
                    }
                }
                throw new Error(errorMessage);
            }

            return data;
        } catch (error) {
            // Utils.showToast(error.message, 'error');
            console.error('API Error:', error);
            throw error;
        }
    }

    static get(endpoint) {
        return this.request(endpoint, 'GET');
    }

    static post(endpoint, body) {
        return this.request(endpoint, 'POST', body);
    }

    static put(endpoint, body) {
        return this.request(endpoint, 'PUT', body);
    }

    static delete(endpoint) {
        return this.request(endpoint, 'DELETE');
    }
}

export default Api;
