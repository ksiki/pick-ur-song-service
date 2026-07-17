import axios from 'axios';

const playerApi = axios.create({
    baseURL: '/api/v1/player',
    withCredentials: true,
});

playerApi.interceptors.request.use((config) => {
    const token = localStorage.getItem('player_iframe_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

playerApi.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            console.error('Токен плеера недействителен или просрочен.');
        }
        return Promise.reject(error);
    }
);

export const PlayerService = {
    // === УПРАВЛЕНИЕ ПЛЕЙЛИСТАМИ ===
    async getPlaylists() {
        const response = await playerApi.get('/playlists');
        return response.data;
    },

    async getPlaylistDetails(playlistId) {
        const response = await playerApi.get(`/playlists/${playlistId}`);
        return response.data;
    },

    async createPlaylist(name) {
        const response = await playerApi.post('/playlists', { name });
        return response.data;
    },

    async deletePlaylist(playlistId) {
        const response = await playerApi.delete(`/playlists/${playlistId}`);
        return response.data;
    },

    async addTrackToPlaylist(playlistId, trackData) {
        // trackData должен соответствовать схеме AddPlaylistTrackRequest
        const response = await playerApi.post(`/playlists/${playlistId}/tracks`, trackData);
        return response.data;
    },

    async removeTrackFromPlaylist(playlistId, trackId) {
        const response = await playerApi.delete(`/playlists/${playlistId}/tracks/${trackId}`);
        return response.data;
    },

    // === REST API ПЛЕЕРА И ОЧЕРЕДИ ===
    async getPlayerState() {
        const response = await playerApi.get('/state');
        return response.data;
    },

    async playPlaylist(playlistId) {
        const response = await playerApi.post(`/queue/playlist/${playlistId}`);
        return response.data;
    },

    async addTrackToQueue(trackData) {
        const response = await playerApi.post('/queue/track', trackData);
        return response.data;
    },

    async addTrackNext(trackData) {
        const response = await playerApi.post('/queue/track/next', trackData);
        return response.data;
    },

    async removeTrackFromQueue(queueId) {
        const response = await playerApi.delete(`/queue/track/${queueId}`);
        return response.data;
    },

    async reorderQueue(newOrderQueueIds) {
        const response = await playerApi.put('/queue/reorder', {
            new_order_queue_ids: newOrderQueueIds
        });
        return response.data;
    },

    async skipTrack() {
        const response = await playerApi.post('/queue/skip');
        return response.data;
    },

    async searchTracks(query) {
        const venueId = localStorage.getItem('player_venue_id');

        if (!venueId) {
            console.error('ID заведения не найден. Невозможно выполнить поиск.');
            throw new Error('Venue ID missing');
        }

        const response = await axios.get('/api/v1/storage/search', {
            params: {
                q: query,
                venue_id: venueId,
                limit: 30
            }
        });

        return response.data;
    }
};
