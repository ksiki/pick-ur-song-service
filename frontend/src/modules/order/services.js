import api from '@/api';

export const OrderService = {
    // Реальный запрос в будущем:
    // search(query) { return api.get(`/music/search?q=${query}`); }

    // Пока используем ваш Mock:
    async search(query) {
        return new Promise(resolve => {
            setTimeout(() => {
                if (query.toLowerCase().includes('xxx')) {
                    resolve([]);
                } else {
                    resolve([
                        { id: '1', title: query + ' (Radio Edit)', artist: 'Artist One', cover: 'https://via.placeholder.com/40/222/fff?text=1', explicit: false },
                        { id: '2', title: query + ' (Original Mix)', artist: 'Artist Two', cover: 'https://via.placeholder.com/40/333/fff?text=2', explicit: true },
                        { id: '3', title: query + ' Remix', artist: 'Artist Three', cover: 'https://via.placeholder.com/40/444/fff?text=3', explicit: false }
                    ]);
                }
            }, 800);
        });
    },

    // Реальный запрос в будущем:
    // validate(trackId) { return api.post(`/orders/validate`, { track_id: trackId }); }

    async validate(trackId) {
        return new Promise((resolve, reject) => {
            setTimeout(() => {
                if (trackId === '2') {
                    reject({ response: { data: { detail: "Трек содержит ненормативную лексику (Explicit) и заблокирован заведением." } } });
                } else {
                    resolve({ status: "ok", price: 500 });
                }
            }, 400);
        });
    }
};
