<template>
  <div class="queue-container">

    <div class="search-section" v-click-outside="closeSearch">
      <div class="search-input-wrapper">
        <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="11" cy="11" r="8"></circle>
          <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
        </svg>
        <input
          v-model="searchQuery"
          type="text"
          class="glass-panel search-input"
          placeholder="Поиск треков..."
          @focus="isSearchFocused = true"
        />
      </div>

      <Transition name="fade">
        <div v-if="searchQuery && isSearchFocused" class="search-dropdown glass-panel">

          <div v-if="isSearching" class="empty-results text-muted">
            Ищем треки...
          </div>

          <div v-else-if="searchResults.length === 0" class="empty-results text-muted">
            Ничего не найдено
          </div>

          <div v-for="result in searchResults" :key="result.track_id" class="search-result-item">
            <img :src="result.artwork_url || 'https://picsum.photos/40?random=99'" class="result-cover" alt="cover" />
            <div class="result-details">
              <span class="result-name">{{ result.title }}</span>
              <span class="result-artist">{{ result.artist }}</span>
            </div>

            <div class="result-actions">

              <button class="action-btn" title="Играть без очереди" @click="playNext(result)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <polygon points="5 4 15 12 5 20 5 4"></polygon>
                  <line x1="19" y1="5" x2="19" y2="19"></line>
                </svg>
              </button>

              <button class="action-btn" title="Добавить в очередь" @click="addToQueue(result)">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <line x1="21" y1="6" x2="3" y2="6"></line>
                  <line x1="21" y1="12" x2="3" y2="12"></line>
                  <line x1="14" y1="18" x2="3" y2="18"></line>
                  <line x1="19" y1="16" x2="19" y2="22"></line>
                  <line x1="16" y1="19" x2="22" y2="19"></line>
                </svg>
              </button>

              <div class="playlist-dropdown-wrapper">
                <button class="action-btn" title="Добавить в плейлист" @click.stop="toggleSearchPlaylist(result.track_id)">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M9 18V5l12-2v9"></path>
                    <circle cx="6" cy="18" r="3"></circle>
                    <line x1="19" y1="16" x2="19" y2="22"></line>
                    <line x1="16" y1="19" x2="22" y2="19"></line>
                  </svg>
                </button>

                <div v-if="activeSearchTrackId === result.track_id" class="search-playlist-menu glass-panel" v-click-outside="closeSearchPlaylist">
                  <div class="submenu-title">Выберите плейлист</div>
                  <div class="submenu-scroll">
                    <button
                      v-for="p in playlists"
                      :key="p.id"
                      @click="addToPlaylistFromSearch(result, p.id)"
                    >
                      {{ p.name }}
                    </button>
                    <div v-if="playlists.length === 0" class="empty-playlists">Нет плейлистов</div>
                  </div>
                </div>
              </div>

            </div>
          </div>
        </div>
      </Transition>
    </div>

    <div class="queue-section">
      <h2 class="section-title">Очередь</h2>

      <div
        class="queue-scroll-area"
        ref="scrollContainer"
        @dragover.prevent="onContainerDragOver"
      >
        <div v-if="currentTrack" class="queue-item glass-panel is-current-playing">
          <div style="width: 28px;"></div>
          <img :src="currentTrack.artwork_url || 'https://picsum.photos/48?random=1'" class="queue-cover" alt="cover" />
          <div class="queue-details">
            <div class="queue-name-row">
              <span class="queue-name">{{ currentTrack.title }}</span>
              <span class="track-badge badge-playing">Сейчас играет</span>
            </div>
            <span class="queue-artist">{{ currentTrack.artist }}</span>
          </div>
          <div class="playing-indicator">
            <span class="eq-bar"></span><span class="eq-bar"></span><span class="eq-bar"></span>
          </div>
        </div>

        <TransitionGroup
          name="queue-list"
          tag="div"
          class="queue-list"
          :class="{ 'is-dragging-active': draggedItemIndex !== null }"
        >
          <div
            v-for="(track, index) in queue"
            :key="track.queue_id"
            class="queue-item glass-panel"
            :class="{ 'is-dragging': draggedItemIndex === index }"
            draggable="true"
            :data-index="index"
            @dragstart="onDragStart(index, $event)"
            @dragover.prevent="onDragOver(index)"
            @dragend="onDragEnd"
            @drop="onDrop"
          >
            <div
              class="drag-handle"
              title="Перетащить"
              @touchstart.stop.prevent="onTouchStart(index, $event)"
              @touchmove.prevent="onTouchMove"
              @touchend="onTouchEnd"
              @touchcancel="onTouchEnd"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="4" y1="8" x2="20" y2="8"></line>
                <line x1="4" y1="16" x2="20" y2="16"></line>
              </svg>
            </div>

            <img :src="track.artwork_url || 'https://picsum.photos/48?random=2'" class="queue-cover" alt="cover" />

            <div class="queue-details">
              <div class="queue-name-row">
                <span class="queue-name">{{ track.title }}</span>
                <span v-if="track.source_type === 'VIP_ORDER'" class="track-badge badge-vip">VIP</span>
                <span v-else-if="track.source_type === 'ORDER'" class="track-badge badge-order">Заказ</span>
                <span v-else-if="track.source_type === 'BACKGROUND'" class="track-badge badge-playlist">Фон</span>
              </div>
              <span class="queue-artist">{{ track.artist }}</span>
            </div>

            <button class="delete-btn" @click="requestDelete(track)">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="3 6 5 6 21 6"></polyline>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
              </svg>
            </button>
          </div>
        </TransitionGroup>

        <div v-if="queue.length === 0 && !currentTrack" class="empty-state text-muted">
          Очередь пуста
        </div>
      </div>
    </div>

    <ConfirmModal ref="confirmModal" />
  </div>
</template>

<script setup>
import { ref, onMounted, inject, watch } from 'vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import { PlayerService } from '../services'
import { useNotification } from '../../../composables/useNotification'

const { showNotification } = useNotification()
const currentTrack = inject('currentTrack')
const wsLastMessage = inject('wsLastMessage')

const vClickOutside = {
  mounted(el, binding) {
    el.clickOutsideEvent = (event) => {
      if (!(el === event.target || el.contains(event.target))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el.clickOutsideEvent)
  },
  unmounted(el) {
    document.removeEventListener('click', el.clickOutsideEvent)
  }
}

watch(wsLastMessage, (newMsg) => {
  if (newMsg) loadQueueState()
})

const searchQuery = ref('')
const isSearchFocused = ref(false)
const isSearching = ref(false)
const searchResults = ref([])
const activeSearchTrackId = ref(null)

const confirmModal = ref(null)
const scrollContainer = ref(null)
const playlists = ref([])

// --- DEBOUNCED SEARCH ---
let searchTimeout = null

watch(searchQuery, (newQuery) => {
  if (!newQuery.trim()) {
    searchResults.value = []
    isSearching.value = false
    return
  }

  isSearching.value = true
  clearTimeout(searchTimeout)

  searchTimeout = setTimeout(async () => {
    try {
      // ПРЕДПОЛАГАЕТСЯ, ЧТО ТЫ ДОБАВИШЬ ЭТОТ МЕТОД В services.js:
      // В router_s.py эндпоинт поиска находится по пути /search
      // (с префиксом /storage из api.py это /api/v1/storage/search)
      const res = await PlayerService.searchTracks(newQuery.trim())
      searchResults.value = res.items || []
    } catch (error) {
      console.error('[PlayerQueue] Ошибка поиска:', error)
      showNotification('Ошибка поиска', 'Не удалось загрузить результаты поиска', 'error')
      searchResults.value = []
    } finally {
      isSearching.value = false
    }
  }, 500) // 500мс задержка
})

const closeSearch = () => {
  isSearchFocused.value = false
  activeSearchTrackId.value = null
}

const toggleSearchPlaylist = (trackId) => {
  activeSearchTrackId.value = activeSearchTrackId.value === trackId ? null : trackId
}
const closeSearchPlaylist = () => {
  activeSearchTrackId.value = null
}

// -- РАБОТА С ОЧЕРЕДЬЮ И API --
const queue = ref([])

const loadQueueState = async () => {
  if (draggedItemIndex.value !== null) return
  try {
    const state = await PlayerService.getPlayerState()
    currentTrack.value = state.currently_playing
    queue.value = state.items || []
  } catch (error) {
    console.error('[PlayerQueue] Ошибка загрузки очереди:', error)
    showNotification('Сбой синхронизации', 'Не удалось загрузить очередь', 'error')
  }
}

const loadPlaylists = async () => {
  try {
    playlists.value = await PlayerService.getPlaylists()
  } catch (e) {
    console.error('Ошибка загрузки плейлистов:', e)
  }
}

onMounted(() => {
  loadQueueState()
  loadPlaylists()
})

const playNext = async (track) => {
  try {
    await PlayerService.addTrackNext({
      track_id: track.track_id,
      track_url: track.track_url,
      title: track.title,
      artist: track.artist,
      duration_ms: track.duration_ms || 0,
      artwork_url: track.artwork_url,
      source_type: 'VIP_ORDER'
    })
    closeSearch()
    await loadQueueState()
    showNotification('Успех', 'Трек будет играть следующим', 'success')
  } catch (error) {
    console.error('[PlayerQueue] Ошибка:', error)
    showNotification('Ошибка', 'Не удалось добавить трек', 'error')
  }
}

const addToQueue = async (track) => {
  try {
    await PlayerService.addTrackToQueue({
      track_id: track.track_id,
      track_url: track.track_url,
      title: track.title,
      artist: track.artist,
      duration_ms: track.duration_ms || 0,
      artwork_url: track.artwork_url,
      source_type: 'ORDER'
    })
    closeSearch()
    await loadQueueState()
    showNotification('Успех', 'Трек добавлен в очередь', 'success')
  } catch (error) {
    console.error('[PlayerQueue] Ошибка:', error)
    showNotification('Ошибка', 'Не удалось добавить в очередь', 'error')
  }
}

const addToPlaylistFromSearch = async (track, playlistId) => {
  try {
    await PlayerService.addTrackToPlaylist(playlistId, {
      track_id: track.track_id,
      track_url: track.track_url,
      title: track.title,
      artist: track.artist,
      duration_ms: track.duration_ms || 0,
      artwork_url: track.artwork_url
    })
    showNotification('Успех', 'Трек сохранен в плейлист', 'success')
  } catch (error) {
    console.error('[PlayerQueue] Ошибка добавления в плейлист:', error)
    showNotification('Ошибка', 'Не удалось сохранить в плейлист', 'error')
  }
  closeSearchPlaylist()
  closeSearch()
}

const requestDelete = async (track) => {
  const isConfirmed = await confirmModal.value.show('Удалить трек?', `Вы уверены, что хотите удалить "${track.title}" из очереди?`)
  if (isConfirmed) {
    try {
      await PlayerService.removeTrackFromQueue(track.queue_id)
      queue.value = queue.value.filter(t => t.queue_id !== track.queue_id)
      showNotification('Удалено', 'Трек убран из очереди', 'success')
    } catch (error) {
      console.error('[PlayerQueue] Ошибка удаления трека:', error)
      showNotification('Ошибка', 'Не удалось удалить трек', 'error')
    }
  }
}

// -- DRAG AND DROP --
const draggedItemIndex = ref(null)
let lastSwapTime = 0
const swapThrottle = 150

const onDragStart = (index, event) => {
  draggedItemIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  setTimeout(() => { event.target.classList.add('is-dragging-ghost') }, 0)
}
const onDragOver = (index) => {
  if (draggedItemIndex.value === null || draggedItemIndex.value === index) return
  const now = Date.now()
  if (now - lastSwapTime < swapThrottle) return
  lastSwapTime = now
  const items = [...queue.value]
  const draggedItem = items[draggedItemIndex.value]
  items.splice(draggedItemIndex.value, 1)
  items.splice(index, 0, draggedItem)
  queue.value = items
  draggedItemIndex.value = index
}
const onDragEnd = async (event) => {
  event.target.classList.remove('is-dragging-ghost')
  if (draggedItemIndex.value !== null) {
    const newOrderIds = queue.value.map(track => track.queue_id)
    try {
      await PlayerService.reorderQueue(newOrderIds)
    } catch (error) {
      console.error('[PlayerQueue] Ошибка сохранения:', error)
      showNotification('Ошибка', 'Не удалось сохранить новый порядок', 'error')
      await loadQueueState()
    }
  }
  draggedItemIndex.value = null
}
const onDrop = () => { draggedItemIndex.value = null }
const onContainerDragOver = (event) => {
  if (draggedItemIndex.value === null || !scrollContainer.value) return
  const rect = scrollContainer.value.getBoundingClientRect()
  const speed = 12
  if (event.clientY < rect.top + 60) scrollContainer.value.scrollTop -= speed
  else if (event.clientY > rect.bottom - 60) scrollContainer.value.scrollTop += speed
}

// -- TOUCH --
const onTouchStart = (index, event) => { draggedItemIndex.value = index; if (navigator.vibrate) navigator.vibrate(40) }
const onTouchMove = (event) => {
  if (draggedItemIndex.value === null) return
  const touch = event.touches[0]
  const targetElement = document.elementFromPoint(touch.clientX, touch.clientY)
  if (!targetElement) return
  const queueItem = targetElement.closest('.queue-item')
  if (queueItem) {
    const hoverIndex = parseInt(queueItem.getAttribute('data-index'))
    if (!isNaN(hoverIndex) && hoverIndex !== draggedItemIndex.value) onDragOver(hoverIndex)
  }
  if (scrollContainer.value) {
    const rect = scrollContainer.value.getBoundingClientRect()
    if (touch.clientY < rect.top + 60) scrollContainer.value.scrollTop -= 12
    else if (touch.clientY > rect.bottom - 60) scrollContainer.value.scrollTop += 12
  }
}
const onTouchEnd = () => { onDragEnd({ target: { classList: { remove: () => {} } } }) }
</script>

<style scoped>
.queue-container { display: flex; flex-direction: column; height: 100%; gap: 24px; min-height: 0; }
.search-section { position: relative; z-index: 20; }
.search-input-wrapper { position: relative; display: flex; align-items: center; }
.search-icon { position: absolute; left: 16px; color: var(--text-muted); }
.search-input { width: 100%; height: 52px; padding: 0 16px 0 48px; background: var(--glass-surface); border: 1px solid var(--glass-border); border-radius: 12px; color: var(--text-primary); font-family: inherit; font-size: 15px; outline: none; transition: all 0.2s; }
.search-input:focus { border-color: var(--accent-focus); background: var(--glass-surface-focus); }
.search-dropdown { position: absolute; top: calc(100% + 8px); left: 0; width: 100%; max-height: 300px; overflow-y: auto; border-radius: 12px; padding: 8px; display: flex; flex-direction: column; gap: 4px; background: rgba(10, 14, 20, 0.95); box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
.empty-results { padding: 12px; text-align: center; font-size: 14px; }
.search-result-item { display: flex; align-items: center; padding: 8px; border-radius: 8px; gap: 12px; transition: background 0.2s; }
.search-result-item:hover { background: rgba(255, 255, 255, 0.05); }
.result-cover { width: 40px; height: 40px; border-radius: 6px; object-fit: cover; }
.result-details { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.result-name { font-size: 14px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.result-artist { font-size: 12px; color: var(--text-secondary); }
.result-actions { display: flex; gap: 4px; align-items: center; }
.action-btn { background: transparent; border: none; color: var(--text-secondary); width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: all 0.2s; }
.action-btn:hover { background: rgba(255, 255, 255, 0.1); color: var(--text-primary); transform: scale(1.05); }

/* Подменю плейлистов для поиска */
.playlist-dropdown-wrapper { position: relative; }
.search-playlist-menu { position: absolute; top: 100%; right: 0; z-index: 50; width: 160px; padding: 6px; margin-top: 4px; display: flex; flex-direction: column; background: rgba(15, 20, 30, 0.95); box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
.submenu-title { font-size: 10px; text-transform: uppercase; color: var(--text-secondary); padding: 4px 10px 8px; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 4px; font-weight: 600; }
.submenu-scroll { max-height: 140px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
.submenu-scroll::-webkit-scrollbar { width: 3px; }
.submenu-scroll::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 3px; }
.search-playlist-menu button { background: transparent; border: none; color: var(--text-secondary); padding: 8px 10px; text-align: left; font-size: 13px; font-family: inherit; border-radius: 6px; cursor: pointer; transition: background 0.2s, color 0.2s; width: 100%; }
.search-playlist-menu button:hover { background: rgba(255, 255, 255, 0.06); color: var(--text-primary); }
.empty-playlists { padding: 8px 10px; font-size: 12px; color: var(--text-muted); text-align: center; }

.queue-section { flex: 1; display: flex; flex-direction: column; overflow: hidden; min-height: 0; }
.section-title { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); font-weight: 600; margin-bottom: 12px; flex-shrink: 0; }
.queue-scroll-area { flex: 1; overflow-y: auto; padding-right: 4px; display: flex; flex-direction: column; gap: 8px;}
.queue-scroll-area::-webkit-scrollbar { width: 4px; }
.queue-scroll-area::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
.queue-list { display: flex; flex-direction: column; gap: 8px; padding-bottom: 24px; }
.queue-item { display: flex; align-items: center; padding: 12px; gap: 12px; transition: all 0.3s ease; cursor: grab; }
.queue-item:active { cursor: grabbing; }

.is-current-playing { border-color: rgba(0, 240, 255, 0.4); background: rgba(0, 240, 255, 0.05); cursor: default; margin-bottom: 16px; box-shadow: 0 4px 12px rgba(0, 240, 255, 0.1); }
.is-current-playing:active { cursor: default; }
.playing-indicator { display: flex; align-items: flex-end; gap: 3px; height: 16px; padding: 0 10px; }
.playing-indicator .eq-bar { width: 3px; background: var(--accent-focus); border-radius: 2px; animation: eq-bounce 1s infinite alternate ease-in-out; }
.playing-indicator .eq-bar:nth-child(1) { height: 8px; animation-delay: 0.1s; }
.playing-indicator .eq-bar:nth-child(2) { height: 16px; animation-delay: 0.3s; }
.playing-indicator .eq-bar:nth-child(3) { height: 10px; animation-delay: 0.5s; }

.queue-item.is-dragging { box-shadow: 0 12px 24px rgba(0, 0, 0, 0.5); transform: scale(1.02); border-color: var(--accent-focus); z-index: 10; }
.is-dragging-ghost { opacity: 0; }
.is-dragging-active .queue-item { transition: none !important; }
.drag-handle { color: var(--text-muted); cursor: grab; display: flex; align-items: center; justify-content: center; padding: 4px; transition: color 0.2s; }
.queue-item:hover .drag-handle { color: var(--text-secondary); }
.queue-cover { width: 48px; height: 48px; border-radius: 8px; object-fit: cover; }
.queue-details { flex: 1; display: flex; flex-direction: column; min-width: 0; gap: 2px; }
.queue-name-row { display: flex; align-items: center; gap: 8px; }
.queue-name { font-size: 15px; font-weight: 600; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

.track-badge { font-size: 10px; font-weight: 700; text-transform: uppercase; padding: 2px 6px; border-radius: 4px; letter-spacing: 0.5px; white-space: nowrap; }
.badge-playing { background: rgba(0, 240, 255, 0.15); color: var(--accent-focus); border: 1px solid rgba(0, 240, 255, 0.3); }
.badge-vip { background: rgba(255, 0, 85, 0.15); color: var(--accent-primary); border: 1px solid rgba(255, 0, 85, 0.3); }
.badge-order { background: rgba(245, 158, 11, 0.15); color: var(--status-warning); border: 1px solid rgba(245, 158, 11, 0.3); }
.badge-playlist { background: rgba(255, 255, 255, 0.05); color: var(--text-secondary); border: 1px solid var(--glass-border); }

.queue-artist { font-size: 13px; color: var(--text-secondary); }
.delete-btn { background: transparent; border: none; color: var(--text-muted); width: 36px; height: 36px; border-radius: 50%; cursor: pointer; display: flex; align-items: center; justify-content: center; transition: all 0.2s; }
.queue-item:hover .delete-btn { color: var(--text-secondary); }
.delete-btn:hover { background: rgba(239, 68, 68, 0.15); color: var(--status-error) !important; }

.queue-list-enter-active, .queue-list-leave-active { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.queue-list-move { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.queue-list-enter-from { opacity: 0; transform: translateY(-20px); }
.queue-list-leave-to { opacity: 0; transform: translateX(30px); }
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

@keyframes eq-bounce { 0% { transform: scaleY(0.3); } 100% { transform: scaleY(1); } }
</style>
