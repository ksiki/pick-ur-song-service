import axios from 'axios';

const api = axios.create({
    baseURL: '/api/v1',
    withCredentials: true,
});

let accessToken = null;
let isRefreshing = false;
let failedQueue = [];

export const setAccessToken = (token) => {
    accessToken = token;
};

const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
        if (error) {
            prom.reject(error);
        } else {
            prom.resolve(token);
        }
    });
    failedQueue = [];
};

api.interceptors.request.use((config) => {
    if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config;

        if (error.response?.status === 401 && !originalRequest._isRetry) {
            if (originalRequest.url.includes('/auth/login')) {
                return Promise.reject(error);
            }

            if (isRefreshing) {
                return new Promise(function(resolve, reject) {
                    failedQueue.push({ resolve, reject });
                }).then(token => {
                    originalRequest.headers['Authorization'] = 'Bearer ' + token;
                    return api.request(originalRequest);
                }).catch(err => {
                    return Promise.reject(err);
                });
            }

            originalRequest._isRetry = true;
            isRefreshing = true;

            try {
                const { data } = await axios.post('/api/v1/auth/refresh', {}, { withCredentials: true });
                setAccessToken(data.access_token);

                processQueue(null, data.access_token);

                originalRequest.headers['Authorization'] = `Bearer ${data.access_token}`;
                return api.request(originalRequest);
            } catch (refreshError) {
                processQueue(refreshError, null);

                setAccessToken(null);
                localStorage.removeItem('is_logged_in');
                window.location.href = '/auth/login';
                throw refreshError;
            } finally {
                isRefreshing = false;
            }
        }
        return Promise.reject(error);
    }
);

export default api;
