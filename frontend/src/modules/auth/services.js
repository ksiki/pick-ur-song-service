import api, { setAccessToken } from '@/api';

export const AuthService = {
    register(email, password) {
        return api.post('/auth/register', { email, password });
    },

    login(email, password) {
        return api.post('/auth/login', { email, password });
    },

    async verifyLoginOtp(email, code) {
        const response = await api.post('/auth/login/verify', { email, code });
        setAccessToken(response.data.access_token);

        localStorage.setItem('is_logged_in', 'true');

        return response.data;
    },

    onboarding(data) {
        return api.post('/auth/onboarding', data);
    },

    async logout() {
        setAccessToken(null);
    },

    async verify(token) {
        const response = await api.post('/auth/verify-email', { token });
        setAccessToken(response.data.access_token);
        localStorage.setItem('is_logged_in', 'true');

        return response.data;
    }
};
