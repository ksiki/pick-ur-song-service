export class PlayerWebSocketService {
  constructor(options) {
    this.ws = null;
    this.pingInterval = null;
    this.reconnectTimer = null;

    this.onMessage = options.onMessage || (() => {});
    this.onStatusChange = options.onStatusChange || (() => {});
    this.onError = options.onError || (() => {});

    this.shouldReconnect = true;
    this.reconnectDelay = 5000;
  }

  connect() {
    const token = localStorage.getItem('player_iframe_token');
    if (!token) {
      this.onError('Ошибка авторизации', 'Токен доступа к плееру не найден');
      return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/v1/player/ws?token=${token}`;

    this.ws = new WebSocket(wsUrl);

    this.ws.onopen = () => {
      console.log('[WS] Соединение установлено');
      this.onStatusChange(true);
      this.startPing();
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        if (data.type === 'PONG') return;

        this.onMessage(data);
      } catch (e) {
        console.error('[WS] Ошибка парсинга сообщения:', e);
      }
    };

    this.ws.onclose = (event) => {
      console.log(`[WS] Соединение закрыто. Код: ${event.code}`);
      this.onStatusChange(false);
      this.stopPing();

      if (event.code === 1008) {
        this.shouldReconnect = false;
        this.onError('Сессия прервана', 'Плеер был запущен на другом устройстве или вкладке.');
        return;
      }

      if (this.shouldReconnect) {
        console.log(`[WS] Переподключение через ${this.reconnectDelay / 1000}с...`);
        clearTimeout(this.reconnectTimer);
        this.reconnectTimer = setTimeout(() => this.connect(), this.reconnectDelay);
      }
    };

    this.ws.onerror = (error) => {
      console.error('[WS] Ошибка соединения:', error);
    };
  }

  startPing() {
    this.stopPing();
    this.pingInterval = setInterval(() => {
      this.send({ type: 'PING' });
    }, 20000);
  }

  stopPing() {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }

  send(data) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('[WS] Попытка отправить сообщение при закрытом соединении', data);
    }
  }

  disconnect() {
    this.shouldReconnect = false;
    this.stopPing();
    clearTimeout(this.reconnectTimer);
    if (this.ws) {
      this.ws.close();
    }
  }
}
