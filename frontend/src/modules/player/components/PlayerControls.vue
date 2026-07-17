<template>
  <div class="controls-container">

    <div class="venue-badge" v-if="venueName">
      <span class="venue-label">Играет в</span>
      <span class="venue-value">{{ venueName }}</span>
      <span class="venue-address" v-if="venueAddress" :title="venueAddress">
        {{ venueAddress }}
      </span>
    </div>

    <div class="player-toggle-wrapper">
      <span class="toggle-label" :class="{ 'is-active': isPlayerActive }">
        {{ isPlayerActive ? 'Плеер работает' : 'Включить плеер' }}
      </span>
      <div
        class="custom-toggle"
        :class="{ 'active': isPlayerActive }"
        @click="togglePlayerState"
      >
        <div class="toggle-thumb"></div>
      </div>
    </div>

    <div class="stream-source" :class="{ 'websocket': isWsConnected, 'disconnected': !isWsConnected }">
      <div class="source-indicator"></div>
      <span>Stream: {{ isWsConnected ? 'Online' : 'Offline' }}</span>
    </div>

    <div class="cover-wrapper" :class="{ 'is-playing': isPlaying }">
      <img :src="currentTrack?.artwork_url || 'https://picsum.photos/400?random=50'" alt="Cover" class="track-cover-large" />
    </div>

    <div class="track-info">
      <div class="title-row">
        <div class="eq-spacer"></div>
        <h2 class="track-title">{{ currentTrack?.title || 'Очередь пуста' }}</h2>
        <div class="mini-eq" :class="{ 'is-active': isPlaying }">
          <span class="eq-bar"></span>
          <span class="eq-bar"></span>
          <span class="eq-bar"></span>
          <span class="eq-bar"></span>
        </div>
      </div>
      <p class="track-artist">{{ currentTrack?.artist || 'Добавьте треки для воспроизведения' }}</p>
    </div>

    <div class="sc-widget-wrapper glass-panel" :class="{ 'is-disabled': !isPlayerActive || !currentTrack?.track_url }">
      <iframe
        ref="scWidgetIframe"
        width="100%"
        height="120"
        scrolling="no"
        frameborder="no"
        allow="autoplay"
        src="https://w.soundcloud.com/player/?url=https%3A//api.soundcloud.com/tracks/293&color=%23ff0055&auto_play=false&hide_related=true&show_comments=false&show_user=false&show_reposts=false&show_teaser=false&visual=false&show_artwork=false">
      </iframe>
    </div>

    <div class="custom-actions-row">

      <button class="skip-btn" @click="nextTrack" :disabled="!isPlayerActive || !currentTrack" title="Следующий трек">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
          <path d="M6 18l8.5-6L6 6v12zM16 6v12h2V6h-2z"/>
        </svg>
      </button>

      <div class="volume-section">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="volume-icon">
          <polygon points="11 5 6 9 2 9 2 15 6 15 11 19 11 5"></polygon>
          <path d="M15.54 8.46a5 5 0 0 1 0 7.07"></path>
          <path d="M19.07 4.93a10 10 0 0 1 0 14.14"></path>
        </svg>

        <div class="progress-bar-container volume-bar" :class="{ 'is-disabled': !isPlayerActive }" @click="setVolume">
          <div class="progress-bar-bg"></div>
          <div class="progress-bar-fill" :style="{ width: volume + '%' }">
            <div class="progress-thumb"></div>
          </div>
        </div>
      </div>

    </div>

    <ConfirmModal ref="confirmModal" />
  </div>
</template>

<script setup>
import { ref, inject, onMounted, watch } from 'vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import { PlayerService } from '../services'

const isPlayerActive = inject('isPlayerActive')
const venueName = inject('venueName')
const venueAddress = inject('venueAddress')
const isWsConnected = inject('isWsConnected')
const currentTrack = inject('currentTrack')
const sendWsMessage = inject('sendWsMessage')

const confirmModal = ref(null)
const isPlaying = ref(false)
const volume = ref(70)

// SoundCloud Widget Ссылки
const scWidgetIframe = ref(null)
let scWidget = null

// --- ВЗАИМОДЕЙСТВИЕ С SOUNDCLOUD API И SOCKET-КОМАНДАМИ ---

const togglePlayerState = () => {
  isPlayerActive.value = !isPlayerActive.value

  if (!isPlayerActive.value && scWidget) {
    scWidget.pause() // Гасим виджет сразу, если бармен отключил плеер в UI
  }
}

const setVolume = (e) => {
  if (!isPlayerActive.value || !scWidget) return

  const rect = e.currentTarget.getBoundingClientRect()
  let percent = (e.clientX - rect.left) / rect.width
  percent = Math.max(0, Math.min(1, percent))

  volume.value = Math.round(percent * 100)
  scWidget.setVolume(volume.value)
}

// Передача события завершения песни в сокет
const handleTrackFinished = () => {
  if (!isPlayerActive.value) return

  sendWsMessage({
    type: 'TRACK_ENDED',
    track_id: currentTrack.value?.track_id,
    order_id: currentTrack.value?.order_id || null
  })
}

// Запрос на пропуск трека (через REST API бэкенда)
const nextTrack = async () => {
  if (!isPlayerActive.value) return

  const source = currentTrack.value?.source_type
  const isOrder = source === 'ORDER' || source === 'VIP_ORDER'

  if (isOrder) {
    const isConfirmed = await confirmModal.value.show(
      'Пропустить заказ?',
      `Трек "${currentTrack.value.title}" был заказан гостем. Вы уверены, что хотите его скипнуть?`
    )
    if (!isConfirmed) return
  }

  try {
    await PlayerService.skipTrack()
  } catch (error) {
    console.error('[Player] Не удалось пропустить трек:', error)
  }
}

// Наблюдатель за изменением стейта текущего трека с бэкенда
watch(() => currentTrack.value, (newTrack) => {
  if (!newTrack || !newTrack.track_url || !scWidget) return

  // Загружаем новый URL в SoundCloud Widget
  scWidget.load(newTrack.track_url, {
    color: '#ff0055',
    auto_play: isPlayerActive.value, // Играть сразу, если плеер в режиме «Работает»
    hide_related: true,
    show_comments: false,
    show_user: false,
    show_reposts: false,
    show_teaser: false,
    visual: false,
    show_artwork: false
  })
}, { deep: true })

// Наблюдатель за состоянием активации плеера барменом
watch(isPlayerActive, (isActive) => {
  if (!scWidget) return
  if (isActive) {
    scWidget.play()
  } else {
    scWidget.pause()
  }
})

// --- ИНИЦИАЛИЗАЦИЯ SOUNDCLOUD API ---
onMounted(() => {
  const initWidget = () => {
    scWidget = window.SC.Widget(scWidgetIframe.value)

    scWidget.bind(window.SC.Widget.Events.READY, () => {
      console.log('SC Widget успешно проинициализирован')
      scWidget.setVolume(volume.value)

      // Если при монтировании у нас уже определен текущий играющий трек — загрузим его
      if (currentTrack.value?.track_url) {
        scWidget.load(currentTrack.value.track_url, {
          color: '#ff0055',
          auto_play: isPlayerActive.value,
          hide_related: true,
          show_comments: false,
          show_user: false,
          show_reposts: false,
          show_teaser: false,
          visual: false,
          show_artwork: false
        })
      }
    })

    scWidget.bind(window.SC.Widget.Events.PLAY, () => {
      isPlaying.value = true
    })

    scWidget.bind(window.SC.Widget.Events.PAUSE, () => {
      isPlaying.value = false
    })

    // При завершении трека отправляем событие бэкенду по сокету
    scWidget.bind(window.SC.Widget.Events.FINISH, () => {
      console.log('Стрим трека завершен')
      handleTrackFinished()
    })
  }

  // Динамически цепляем скрипт SoundCloud API, если он отсутствует в глобальном window
  if (!window.SC) {
    const script = document.createElement('script')
    script.src = 'https://w.soundcloud.com/player/api.js'
    script.onload = initWidget
    document.body.appendChild(script)
  } else {
    initWidget()
  }
})
</script>

<style scoped>
.controls-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  gap: 28px;
  max-width: 340px;
  margin: 0 auto;
}

/* --- ПЛАШКА ЗАВЕДЕНИЯ --- */
.venue-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  margin-bottom: -16px;
  width: 100%;
}

.venue-label {
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: 1.5px;
  color: var(--text-muted);
  font-weight: 600;
}

.venue-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--accent-focus);
  text-align: center;
  text-shadow: 0 0 12px rgba(0, 240, 255, 0.25);
}

.venue-address {
  font-size: 12px;
  color: var(--text-secondary);
  text-align: center;
  max-width: 280px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  opacity: 0.8;
}

.stream-source {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 6px 14px;
  border-radius: 100px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.5px;
  text-transform: uppercase;
  transition: all 0.3s ease;
  min-width: 280px;
}

/* Статус WS подключен */
.stream-source.websocket {
  color: var(--accent-focus);
  border-color: rgba(0, 240, 255, 0.2);
}
.stream-source.websocket .source-indicator {
  background: var(--accent-focus);
  box-shadow: 0 0 8px var(--accent-focus);
}

/* Статус WS отключен */
.stream-source.disconnected {
  color: var(--status-error);
  border-color: rgba(239, 68, 68, 0.2);
}
.stream-source.disconnected .source-indicator {
  background: var(--status-error);
  box-shadow: 0 0 8px var(--status-error);
}

.source-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  transition: all 0.3s ease;
}

.cover-wrapper { position: relative; width: 100%; aspect-ratio: 1 / 1; border-radius: 16px; overflow: hidden; box-shadow: 0 16px 32px rgba(0,0,0,0.5); transition: all 0.3s ease; border: 2px solid transparent; }
.cover-wrapper.is-playing { border-color: rgba(255, 0, 85, 0.4); animation: breathe 2s infinite alternate ease-in-out; }

@keyframes breathe {
  0% { box-shadow: 0 16px 32px rgba(0,0,0,0.5), 0 0 10px rgba(255, 0, 85, 0.2); transform: scale(1); }
  100% { box-shadow: 0 16px 32px rgba(0,0,0,0.5), 0 0 30px rgba(255, 0, 85, 0.6); transform: scale(1.02); }
}

.track-cover-large { width: 100%; height: 100%; object-fit: cover; }

.track-info { width: 100%; text-align: center; display: flex; flex-direction: column; gap: 8px; margin-top: -10px; }
.title-row { display: flex; align-items: center; justify-content: center; gap: 12px; width: 100%; }
.track-title { font-size: 24px; font-weight: 600; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; min-width: 0; }
.track-artist { font-size: 16px; color: var(--text-secondary); }
.eq-spacer { width: 21px; flex-shrink: 0; }
.mini-eq { width: 21px; flex-shrink: 0; display: flex; align-items: flex-end; gap: 3px; height: 16px; opacity: 0; transition: opacity 0.2s; }
.mini-eq.is-active { opacity: 1; }
.eq-bar { width: 3px; background: var(--accent-primary); border-radius: 2px; animation: eq-bounce 1s infinite alternate ease-in-out; }
.mini-eq .eq-bar:nth-child(1) { height: 6px; animation-delay: 0.1s; }
.mini-eq .eq-bar:nth-child(2) { height: 16px; animation-delay: 0.3s; }
.mini-eq .eq-bar:nth-child(3) { height: 10px; animation-delay: 0.5s; }
.mini-eq .eq-bar:nth-child(4) { height: 14px; animation-delay: 0.2s; }

@keyframes eq-bounce { 0% { transform: scaleY(0.3); } 100% { transform: scaleY(1); } }

/* --- ВИДИМЫЙ ВИДЖЕТ SC --- */
.sc-widget-wrapper {
  width: 100%;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  align-items: center;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  transition: opacity 0.3s ease;
}

.sc-widget-wrapper iframe {
  display: block;
}

/* --- КАСТОМНАЯ ПАНЕЛЬ СКИПА И ГРОМКОСТИ --- */
.custom-actions-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  gap: 16px;
}

.skip-btn {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--glass-border);
  color: var(--text-primary);
  border-radius: 12px;
  width: 52px;
  height: 52px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  flex-shrink: 0;
}
.skip-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  transform: scale(1.05);
}
.skip-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.volume-section {
  flex-grow: 1;
  display: flex;
  align-items: center;
  gap: 12px;
  background: var(--glass-surface);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  height: 52px;
  padding: 0 16px;
}
.volume-icon { color: var(--text-secondary); flex-shrink: 0; transition: color 0.2s; }
.volume-section:hover .volume-icon { color: var(--text-primary); }

.progress-bar-container { flex: 1; height: 24px; display: flex; align-items: center; cursor: pointer; position: relative; }
.progress-bar-bg { width: 100%; height: 4px; background: rgba(255, 255, 255, 0.1); border-radius: 2px; position: absolute; }
.progress-bar-fill { height: 4px; background: var(--accent-primary); border-radius: 2px; position: absolute; left: 0; transition: width 0.1s linear; }
.progress-thumb { width: 12px; height: 12px; background: #fff; border-radius: 50%; position: absolute; right: -6px; top: 50%; transform: translateY(-50%) scale(0); transition: transform 0.2s; box-shadow: 0 0 10px rgba(255, 0, 85, 0.5); }
.progress-bar-container:hover .progress-thumb { transform: translateY(-50%) scale(1); }

/* --- ТОГГЛ ВКЛЮЧЕНИЯ ПЛЕЕРА --- */
.player-toggle-wrapper { display: flex; align-items: center; justify-content: space-between; width: 100%; padding: 12px 20px; background: var(--glass-surface); border: 1px solid var(--glass-border); border-radius: 100px; margin-bottom: -10px; box-shadow: 0 4px 16px rgba(0, 0, 0, 0.2); transition: all 0.3s ease; }
.player-toggle-wrapper:hover { background: rgba(255, 255, 255, 0.05); }
.toggle-label { font-size: 14px; font-weight: 600; color: var(--text-secondary); transition: color 0.3s ease; }
.toggle-label.is-active { color: var(--text-primary); }
.custom-toggle { width: 48px; height: 26px; background: rgba(255, 255, 255, 0.1); border-radius: 13px; position: relative; cursor: pointer; transition: background 0.3s ease, border-color 0.3s ease; border: 1px solid rgba(255, 255, 255, 0.05); }
.custom-toggle.active { background: var(--accent-primary); border-color: var(--accent-primary); box-shadow: 0 0 12px rgba(255, 0, 85, 0.4); }
.toggle-thumb { width: 20px; height: 20px; background: #ffffff; border-radius: 50%; position: absolute; top: 2px; left: 2px; transition: transform 0.3s cubic-bezier(0.4, 0.0, 0.2, 1); box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3); }
.custom-toggle.active .toggle-thumb { transform: translateX(22px); }

/* Выключенные состояния */
.is-disabled { opacity: 0.4; pointer-events: none; }
.progress-bar-container.is-disabled .progress-thumb { display: none; }
.skip-btn:disabled { color: rgba(255, 255, 255, 0.15); border-color: rgba(255, 255, 255, 0.05); cursor: not-allowed; transform: scale(1); }
</style>
