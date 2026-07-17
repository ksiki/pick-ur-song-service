import api from '../../api/index.js';

export const MenuService = {
    async getVenues() {
        // Укажи здесь правильный префикс, если роутер подключен с префиксом (например, /venues)
        const response = await api.get('/venues');
        return response.data;
    },

    /**
     * Получить URL технического домена для плеера с токеном
     * @param {string} venueId - ID выбранного заведения
     */
    async getPlayerUrl(venueId) {
        const response = await api.get(`/venues/${venueId}/player-url`);
        return response.data;
    }
};
