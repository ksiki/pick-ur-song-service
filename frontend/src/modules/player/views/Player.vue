<template>
  <div class="player-layout" :class="{ 'is-mobile': isMobile }">

    <div class="content-area">

      <aside
        class="player-column sidebar-column"
        v-show="!isMobile || activeTab === 'playlists'"
      >
        <header class="app-header player-header" v-if="!isMobile || activeTab === 'playlists'">
          <div class="logo-container">
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M9 18V5L21 3V16" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="6" cy="18" r="3" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
              <circle cx="18" cy="16" r="3" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
            <span class="logo-text">Pick Song</span>
          </div>
        </header>

        <PlayerSidebar />
      </aside>

      <main
        class="player-column queue-column"
        v-show="!isMobile || activeTab === 'queue'"
      >
        <PlayerQueue />
      </main>

      <aside
        class="player-column controls-column"
        v-show="!isMobile || activeTab === 'player'"
      >
        <PlayerControls />
      </aside>

    </div>

    <nav v-if="isMobile" class="bottom-nav glass-panel">
      <button
        class="nav-btn"
        :class="{ active: activeTab === 'playlists' }"
        @click="activeTab = 'playlists'"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <line x1="8" y1="6" x2="21" y2="6"></line>
          <line x1="8" y1="12" x2="21" y2="12"></line>
          <line x1="8" y1="18" x2="21" y2="18"></line>
          <line x1="3" y1="6" x2="3.01" y2="6"></line>
          <line x1="3" y1="12" x2="3.01" y2="12"></line>
          <line x1="3" y1="18" x2="3.01" y2="18"></line>
        </svg>
        <span>Плейлисты</span>
      </button>

      <button
        class="nav-btn"
        :class="{ active: activeTab === 'queue' }"
        @click="activeTab = 'queue'"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
          <polyline points="2 17 12 22 22 17"></polyline>
          <polyline points="2 12 12 17 22 12"></polyline>
        </svg>
        <span>Очередь</span>
      </button>

      <button
        class="nav-btn"
        :class="{ active: activeTab === 'player' }"
        @click="activeTab = 'player'"
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <polygon points="10 8 16 12 10 16 10 8" fill="currentColor"></polygon>
        </svg>
        <span>Плеер</span>
      </button>
    </nav>

    <GlobalAlert />
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue'
import PlayerSidebar from '../components/PlayerSidebar.vue'
import PlayerQueue from '../components/PlayerQueue.vue'
import PlayerControls from '../components/PlayerControls.vue'
import GlobalAlert from '../../../composables/components/GlobalAlert.vue'
import { useNotification } from '../../../composables/useNotification'

import { PlayerWebSocketService } from '../websocket'

const isPlayerActive = ref(false)
const venueName = ref('Загрузка...')
const venueAddress = ref('Загрузка...')
const isWsConnected = ref(false)
const currentTrack = ref(null)
const wsLastMessage = ref(null) // Хранилище последнего входящего WS события

// Пробрасываем состояния вниз
provide('isPlayerActive', isPlayerActive)
provide('venueName', venueName)
provide('venueAddress', venueAddress)
provide('isWsConnected', isWsConnected)
provide('currentTrack', currentTrack)
provide('wsLastMessage', wsLastMessage)

// Функция отправки сообщений (используется в PlayerControls.vue для TRACK_ENDED)
const sendWsMessage = (msg) => {
  if (wsService) {
    wsService.send(msg)
  }
}
provide('sendWsMessage', sendWsMessage)

const { showNotification } = useNotification()
let wsService = null

// --- МОБИЛЬНАЯ АДАПТАЦИЯ ---
const isMobile = ref(false)
const activeTab = ref('queue')

const checkMobile = () => {
  isMobile.value = window.innerWidth <= 768
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)

  const urlParams = new URLSearchParams(window.location.search)
  const tokenFromUrl = urlParams.get('token')
  const venueIdFromUrl = urlParams.get('venue_id')
  const venueNameFromUrl = urlParams.get('venue_name')
  const addressFromUrl = urlParams.get('address')

  if (tokenFromUrl) localStorage.setItem('player_iframe_token', tokenFromUrl)
  if (venueIdFromUrl) localStorage.setItem('player_venue_id', venueIdFromUrl)

  if (venueNameFromUrl) {
    const decodedVenue = decodeURIComponent(venueNameFromUrl)
    localStorage.setItem('player_venue_name', decodedVenue)
    venueName.value = decodedVenue
    showNotification('Успех', `Заведение ${decodedVenue} загружено`, 'success')
  } else {
    venueName.value = localStorage.getItem('player_venue_name') || 'Неизвестное заведение'
  }

  if (addressFromUrl) {
    const decodedAddress = decodeURIComponent(addressFromUrl)
    localStorage.setItem('player_venue_address', decodedAddress)
    venueAddress.value = decodedAddress
  } else {
    venueAddress.value = localStorage.getItem('player_venue_address') || ''
  }

  // Очищаем ссылку от всех параметров, чтобы при F5 URL был чистым
  if (tokenFromUrl || venueIdFromUrl || venueNameFromUrl || addressFromUrl) {
    const newUrl = window.location.origin + window.location.pathname
    window.history.replaceState({}, document.title, newUrl)
  }

  // --- ИНИЦИАЛИЗАЦИЯ WEBSOCKET ---
  wsService = new PlayerWebSocketService({
    onStatusChange: (connected) => {
      isWsConnected.value = connected
      if (connected) {
        showNotification('Связь восстановлена', 'Успешное подключение к серверу', 'success')
      } else {
        showNotification('Потеря связи', 'Соединение прервано...', 'warning')
      }
    },
    onMessage: (payload) => {
      console.log('[WS] Команда с бэкенда:', payload)
      wsLastMessage.value = payload
    },
    onError: (title, message) => {
      showNotification(title, message, 'error')
    }
  })

  wsService.connect()
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
  if (wsService) wsService.disconnect()
})
</script>

<style scoped>
.player-layout {
  display: flex;
  flex-direction: column;
  width: 100vw;
  height: 100vh;
  background-color: #05070A;
  color: var(--text-primary);
  overflow: hidden;
  position: relative;
  z-index: 10;
}

.content-area {
  display: grid;
  grid-template-columns: 320px 1fr 380px;
  flex: 1;
  min-height: 0;
  width: 100%;
}

.player-column {
  display: flex;
  flex-direction: column;
  height: 100%;
  padding: 24px;
  border-right: 1px solid rgba(255, 255, 255, 0.05);
  overflow: hidden;
}

.controls-column {
  border-right: none;
  border-left: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.01);
}

.player-header {
  padding-bottom: 32px;
  justify-content: flex-start;
}

.logo-text {
  font-size: 24px;
  background: linear-gradient(90deg, #FFFFFF, #94A3B8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

@media (max-width: 768px) {
  .content-area {
    display: flex;
    flex-direction: column;
  }

  .player-column {
    width: 100%;
    padding: 16px;
    border: none;
    background: transparent;
  }

  .bottom-nav {
    display: flex;
    justify-content: space-around;
    align-items: center;
    height: 64px;
    background: rgba(10, 14, 20, 0.95);
    border-top: 1px solid var(--glass-border);
    padding-bottom: env(safe-area-inset-bottom, 0px);
    flex-shrink: 0;
    z-index: 50;
    border-radius: 0;
  }

  .nav-btn {
    flex: 1;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4px;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    font-size: 10px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    font-weight: 600;
    cursor: pointer;
    transition: color 0.2s;
    height: 100%;
  }

  .nav-btn:active {
    transform: scale(0.95);
  }

  .nav-btn.active {
    color: var(--accent-primary);
  }
}
</style>
