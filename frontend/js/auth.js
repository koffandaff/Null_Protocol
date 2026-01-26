import Api from './api.js';
import Router from './router.js';

class Auth {
    static async login(email, password) {
        try {
            const formData = { email, password }; // In real OAuth2 form-data is standard, but backend uses JSON here based on endpoints.md
            const response = await Api.post('/auth/login', formData);

            localStorage.setItem('access_token', response.access_token);
            localStorage.setItem('refresh_token', response.refresh_token);
            localStorage.setItem('user', JSON.stringify(response.user));

            return response.user;
        } catch (error) {
            throw error;
        }
    }

    static async signup(userData) {
        return await Api.post('/auth/signup', userData);
    }

    static logout() {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        localStorage.removeItem('user');
        window.location.hash = '/login';
    }

    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    static getUser() {
        return JSON.parse(localStorage.getItem('user'));
    }
}

export default Auth;
