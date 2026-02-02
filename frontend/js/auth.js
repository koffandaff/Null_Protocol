import Api from './api.js';
import Router from './router.js';

class Auth {
    static async login(email, password) {
        try {
            const formData = { email, password };
            const response = await Api.post('/auth/login', formData);

            // If response is null, the disabled modal was shown by Api
            if (!response) {
                return null;
            }

            localStorage.setItem('access_token', response.access_token);
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
        // Call backend to clear cookie
        Api.post('/auth/logout');

        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        window.location.hash = '/login';
    }

    static isAuthenticated() {
        return !!localStorage.getItem('access_token');
    }

    static getUser() {
        return JSON.parse(localStorage.getItem('user'));
    }

    static getCurrentUser() {
        return this.getUser();
    }

    static async forgotPassword(email) {
        return await Api.post('/auth/forgot-password', { email });
    }

    static async verifyOtp(email, otp) {
        return await Api.post('/auth/verify-otp', { email, otp });
    }

    static async resetPassword(email, otp, new_password) {
        return await Api.post('/auth/reset-password', { email, otp, new_password });
    }
}

export default Auth;
