<template>
  <div class="sidebar-container">
    <Transition name="slide-fade" mode="out-in">
      <div v-if="!currentPlaylist" key="playlists" class="view-wrapper">
        <h2 class="section-title">Мои Плейлисты</h2>

        <div class="playlists-list">
          <div
            v-for="playlist in playlists"
            :key="playlist.id"
            class="glass-panel playlist-card"
            :class="{ 'is-active-playlist': playlist.is_active }"
            @click="selectPlaylist(playlist)"
          >
            <div class="playlist-info">
              <span class="playlist-name">{{ playlist.name }}</span>
              <span v-if="playlist.is_active" class="active-label">
                <span class="pulse-dot"></span> Сейчас играет
              </span>
            </div>

            <div class="playlist-actions" @click.stop>
              <button
                class="action-btn play-btn"
                @click="playPlaylist(playlist)"
                :disabled="!isPlayerActive || playlist.is_active"
              >
                <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M8 5v14l11-7z"/>
                </svg>
              </button>
              <button class="action-btn delete-btn" @click="deletePlaylist(playlist)">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <polyline points="3 6 5 6 21 6"></polyline>
                  <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
                </svg>
              </button>
            </div>
          </div>

          <div class="glass-panel create-card" :class="{ 'is-editing': isCreating }">
            <div v-if="!isCreating" class="create-trigger" @click="isCreating = true">
              <span class="plus-icon">+</span>
            </div>
            <div v-else class="create-form">
              <input
                ref="playlistInput"
                v-model="newPlaylistName"
                type="text"
                placeholder="Название плейлиста..."
                @keyup.enter="createPlaylist"
                @keyup.esc="cancelCreate"
              />
              <div class="form-buttons">
                <button class="btn-cancel" @click="cancelCreate">Отмена</button>
                <button class="btn-save" :disabled="!newPlaylistName.trim()" @click="createPlaylist">Создать</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else key="tracks" class="view-wrapper">
        <div class="sidebar-header">
          <button class="back-button" @click="goBack">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="19" y1="12" x2="5" y2="12"></line>
              <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            Назад
          </button>
          <h2 class="playlist-title-view">{{ currentPlaylist.name }}</h2>
        </div>

        <div class="tracks-list">
          <div v-if="currentPlaylist.tracks.length === 0" class="empty-state text-muted">
            В плейлисте пока нет треков
          </div>

          <div
            v-for="track in currentPlaylist.tracks"
            :key="track.id"
            class="track-item"
          >
            <img :src="track.track_artwork_url || 'https://picsum.photos/40?random=1'" class="track-cover" alt="cover" />
            <div class="track-details">
              <span class="track-name">{{ track.track_title }}</span>
              <span class="track-artist">{{ track.track_artist }}</span>
            </div>

            <div class="menu-container">
              <button class="more-btn" @click.stop="toggleTrackMenu(track.id, $event)">
                •••
              </button>

              <div
                v-if="activeTrackMenuId === track.id"
                class="context-menu glass-panel"
                v-click-outside="closeTrackMenu"
              >
                <div v-if="!showPlaylistSelector" class="menu-main">
                  <button @click="executeAction('play-next', track)">
                    <span>Играть без очереди</span>
                  </button>
                  <button @click="executeAction('add-queue', track)">
                    <span>Добавить в очередь</span>
                  </button>
                  <button @click.stop="showPlaylistSelector = true">
                    <span>Добавить в плейлист</span>
                  </button>
                  <button class="danger-action" @click="executeAction('delete-track', track)">
                    <span>Удалить</span>
                  </button>
                </div>

                <div v-else class="menu-submenu">
                  <div class="submenu-header" @click.stop="showPlaylistSelector = false">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <polyline points="15 18 9 12 15 6"></polyline>
                    </svg>
                    <span>Назад</span>
                  </div>
                  <div class="submenu-scroll">
                    <button
                      v-for="p in playlists"
                      :key="p.id"
                      @click="addToPlaylist(track, p.id)"
                      :disabled="p.id === currentPlaylist.id"
                    >
                      {{ p.name }}
                    </button>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
    <ConfirmModal ref="confirmModalRef" />
  </div>
</template>

<script setup>
import { ref, onMounted, inject } from 'vue'
import ConfirmModal from './ui/ConfirmModal.vue'
import { PlayerService } from '../services'

const confirmModalRef = ref(null)
const isPlayerActive = inject('isPlayerActive')

const playlists = ref([])
const currentPlaylist = ref(null)
const isCreating = ref(false)
const newPlaylistName = ref('')
const playlistInput = ref(null)

const activeTrackMenuId = ref(null)
const showPlaylistSelector = ref(false) // Состояние для подменю списка плейлистов

const loadPlaylists = async () => {
  try {
    playlists.value = await PlayerService.getPlaylists()
  } catch (error) {
    console.error('[PlayerSidebar] Ошибка загрузки плейлистов:', error)
  }
}

onMounted(() => {
  loadPlaylists()
})

const selectPlaylist = async (playlist) => {
  try {
    currentPlaylist.value = await PlayerService.getPlaylistDetails(playlist.id)
  } catch (error) {
    console.error('[PlayerSidebar] Ошибка загрузки деталей плейлиста:', error)
  }
}

const createPlaylist = async () => {
  if (!newPlaylistName.value.trim()) return
  try {
    await PlayerService.createPlaylist(newPlaylistName.value.trim())
    await loadPlaylists()
    cancelCreate()
  } catch (error) {
    console.error('[PlayerSidebar] Ошибка создания плейлиста:', error)
  }
}

const cancelCreate = () => {
  isCreating.value = false
  newPlaylistName.value = ''
}

const deletePlaylist = async (playlist) => {
  const isConfirmed = await confirmModalRef.value.show(
    'Удаление плейлиста',
    `Вы действительно хотите удалить плейлист «${playlist.name}»? Это действие нельзя отменить.`
  )
  if (isConfirmed) {
    try {
      await PlayerService.deletePlaylist(playlist.id)
      await loadPlaylists()
    } catch (error) {
      console.error('[PlayerSidebar] Ошибка удаления плейлиста:', error)
    }
  }
}

const playPlaylist = async (playlist) => {
  if (!isPlayerActive.value || playlist.is_active) return
  try {
    await PlayerService.playPlaylist(playlist.id)
    await loadPlaylists()
  } catch (error) {
    console.error('[PlayerSidebar] Ошибка запуска плейлиста:', error)
  }
}

const goBack = () => {
  currentPlaylist.value = null
  closeTrackMenu()
  loadPlaylists()
}

const toggleTrackMenu = (trackId, event) => {
  activeTrackMenuId.value = activeTrackMenuId.value === trackId ? null : trackId
  showPlaylistSelector.value = false // Сбрасываем подменю при открытии
}

const closeTrackMenu = () => {
  activeTrackMenuId.value = null
  showPlaylistSelector.value = false
}

// --- API ВЫЗОВЫ ИЗ КОНТЕКСТНОГО МЕНЮ ---

const executeAction = async (action, track) => {
  closeTrackMenu()

  if (action === 'delete-track' && currentPlaylist.value) {
    try {
      await PlayerService.removeTrackFromPlaylist(currentPlaylist.value.id, track.track_id)
      currentPlaylist.value = await PlayerService.getPlaylistDetails(currentPlaylist.value.id)
    } catch (error) {
      console.error('[PlayerSidebar] Ошибка удаления трека:', error)
    }
  } else if (action === 'play-next') {
    try {
      await PlayerService.addTrackNext({
        track_id: parseInt(track.track_id),
        track_url: track.track_url,
        title: track.track_title,
        artist: track.track_artist,
        duration_ms: track.duration_ms || 0,
        artwork_url: track.track_artwork_url,
        source_type: 'VIP_ORDER'
      })
    } catch (error) {
      console.error('[PlayerSidebar] Ошибка добавления:', error)
    }
  } else if (action === 'add-queue') {
    try {
      await PlayerService.addTrackToQueue({
        track_id: parseInt(track.track_id),
        track_url: track.track_url,
        title: track.track_title,
        artist: track.track_artist,
        duration_ms: track.duration_ms || 0,
        artwork_url: track.track_artwork_url,
        source_type: 'ORDER'
      })
    } catch (error) {
      console.error('[PlayerSidebar] Ошибка добавления в очередь:', error)
    }
  }
}

const addToPlaylist = async (track, targetPlaylistId) => {
  try {
    await PlayerService.addTrackToPlaylist(targetPlaylistId, {
      track_id: parseInt(track.track_id),
      track_url: track.track_url,
      title: track.track_title,
      artist: track.track_artist,
      duration_ms: track.duration_ms || 0,
      artwork_url: track.track_artwork_url
    })
  } catch (error) {
    console.error('[PlayerSidebar] Ошибка копирования в плейлист:', error)
  }
  closeTrackMenu()
}

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
</script>

<style scoped>
.sidebar-container { display: flex; flex-direction: column; flex: 1; overflow-y: auto; padding-right: 4px; }
.sidebar-container::-webkit-scrollbar { width: 4px; }
.sidebar-container::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
.view-wrapper { display: flex; flex-direction: column; gap: 16px; }
.section-title { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: var(--text-secondary); font-weight: 600; margin-bottom: 8px; }
.playlists-list { display: flex; flex-direction: column; gap: 12px; }

.playlist-card {
  display: flex; justify-content: space-between; align-items: center; padding: 16px;
  cursor: pointer; transition: transform 0.15s ease, background 0.2s ease, border-color 0.2s ease, box-shadow 0.3s ease;
  border: 1px solid var(--glass-border);
}
.playlist-card:hover { background: rgba(255, 255, 255, 0.08); border-color: rgba(255, 255, 255, 0.15); }
.playlist-card:active { transform: scale(0.97); }
.playlist-card.is-active-playlist {
  border-color: var(--accent-primary); background: rgba(255, 0, 85, 0.05);
  animation: neon-pulse 2.5s infinite alternate ease-in-out;
}
@keyframes neon-pulse {
  0% { box-shadow: 0 0 4px rgba(255, 0, 85, 0.1); }
  100% { box-shadow: 0 0 16px rgba(255, 0, 85, 0.4); border-color: rgba(255, 0, 85, 0.8); }
}

.playlist-info { display: flex; flex-direction: column; gap: 6px; }
.playlist-name { font-weight: 600; font-size: 15px; color: var(--text-primary); }
.active-label {
  font-size: 10px; color: var(--accent-primary); text-transform: uppercase;
  letter-spacing: 0.5px; font-weight: 700; display: flex; align-items: center; gap: 6px;
}
.pulse-dot {
  width: 6px; height: 6px; background-color: var(--accent-primary); border-radius: 50%;
  box-shadow: 0 0 8px var(--accent-primary); animation: dot-blink 1s infinite alternate ease-in-out;
}
@keyframes dot-blink {
  0% { opacity: 0.4; transform: scale(0.8); }
  100% { opacity: 1; transform: scale(1.2); }
}

.playlist-actions { display: flex; gap: 8px; }
.action-btn { background: transparent; border: none; color: var(--text-secondary); width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; cursor: pointer; transition: background 0.2s, color 0.2s; }
.play-btn:hover:not(:disabled) { background: rgba(255, 255, 255, 0.1); color: var(--text-primary); }
.delete-btn:hover { background: rgba(239, 68, 68, 0.15); color: var(--status-error); }
.play-btn:disabled { color: var(--accent-primary); cursor: default; opacity: 1; }

.create-card { border-style: dashed; border-color: rgba(255, 255, 255, 0.15); min-height: 56px; display: flex; align-items: center; justify-content: center; transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1); }
.create-card:not(.is-editing):hover { background: rgba(255, 255, 255, 0.06); border-color: var(--accent-primary); }
.create-trigger { width: 100%; height: 52px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
.plus-icon { font-size: 24px; color: var(--text-secondary); transition: color 0.2s; }
.create-card:hover .plus-icon { color: var(--text-primary); }
.create-form { width: 100%; padding: 12px; display: flex; flex-direction: column; gap: 10px; }
.create-form input { width: 100%; background: rgba(0, 0, 0, 0.2); border: 1px solid var(--glass-border); border-radius: 8px; padding: 8px 12px; color: #fff; font-family: inherit; font-size: 14px; outline: none; }
.create-form input:focus { border-color: var(--accent-focus); }
.form-buttons { display: flex; justify-content: flex-end; gap: 8px; }
.form-buttons button { padding: 6px 12px; border-radius: 6px; font-size: 12px; font-weight: 600; cursor: pointer; border: none; font-family: inherit; transition: background 0.2s, transform 0.1s; }
.form-buttons button:active { transform: scale(0.95); }
.btn-cancel { background: transparent; color: var(--text-secondary); }
.btn-cancel:hover { background: rgba(255, 255, 255, 0.05); color: var(--text-primary); }
.btn-save { background: var(--accent-primary); color: #fff; }
.btn-save:hover:not(:disabled) { background: var(--accent-hover); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }

.sidebar-header { display: flex; flex-direction: column; gap: 12px; margin-bottom: 8px; }
.back-button { background: transparent; border: none; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; cursor: pointer; font-size: 14px; font-family: inherit; align-self: flex-start; transition: color 0.2s; padding: 4px 0; }
.back-button:hover { color: var(--text-primary); }
.playlist-title-view { font-size: 20px; font-weight: 600; color: var(--text-primary); }
.tracks-list { display: flex; flex-direction: column; gap: 8px; }
.track-item { display: flex; align-items: center; padding: 8px; border-radius: 12px; gap: 12px; transition: background 0.2s; position: relative; }
.track-item:hover { background: rgba(255, 255, 255, 0.04); }
.track-cover { width: 40px; height: 40px; border-radius: 8px; object-fit: cover; }
.track-details { display: flex; flex-direction: column; flex: 1; min-width: 0; }
.track-name { font-weight: 600; font-size: 14px; color: var(--text-primary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.track-artist { font-size: 12px; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* --- СТИЛИ КОНТЕКСТНОГО МЕНЮ И ПОДМЕНЮ --- */
.menu-container { position: relative; }
.more-btn { background: transparent; border: none; color: var(--text-muted); cursor: pointer; padding: 8px; font-size: 12px; transition: color 0.2s; }
.track-item:hover .more-btn, .more-btn:focus { color: var(--text-primary); }

.context-menu { position: absolute; top: 100%; right: 0; z-index: 50; width: 160px; padding: 6px; display: flex; flex-direction: column; background: rgba(15, 20, 30, 0.95); box-shadow: 0 10px 25px rgba(0,0,0,0.5); overflow: hidden; }
.menu-main { display: flex; flex-direction: column; gap: 2px; }
.context-menu button { background: transparent; border: none; color: var(--text-secondary); padding: 8px 10px; text-align: left; font-size: 13px; font-family: inherit; border-radius: 6px; cursor: pointer; transition: background 0.2s, color 0.2s; width: 100%; }
.context-menu button:hover:not(:disabled) { background: rgba(255, 255, 255, 0.06); color: var(--text-primary); }
.context-menu button:disabled { opacity: 0.4; cursor: not-allowed; }
.context-menu button.danger-action:hover { background: rgba(239, 68, 68, 0.15); color: var(--status-error); }

.menu-submenu { display: flex; flex-direction: column; }
.submenu-header { display: flex; align-items: center; gap: 6px; padding: 6px 10px 10px; color: var(--text-secondary); font-size: 11px; font-weight: 600; text-transform: uppercase; cursor: pointer; border-bottom: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 4px; transition: color 0.2s; }
.submenu-header:hover { color: var(--text-primary); }
.submenu-scroll { max-height: 140px; overflow-y: auto; display: flex; flex-direction: column; gap: 2px; }
.submenu-scroll::-webkit-scrollbar { width: 3px; }
.submenu-scroll::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.2); border-radius: 3px; }

.slide-fade-enter-active, .slide-fade-leave-active { transition: all 0.2s ease; }
.slide-fade-enter-from { opacity: 0; transform: translateX(-10px); }
.slide-fade-leave-to { opacity: 0; transform: translateX(10px); }
</style>
