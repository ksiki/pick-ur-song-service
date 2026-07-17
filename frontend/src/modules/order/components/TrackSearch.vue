<template>
  <div class="search-container">
    <div class="input-wrapper glass-panel">
      <svg class="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"></circle>
        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
      </svg>
      <input type="text" v-model="searchQuery" @input="handleInput" @focus="handleFocus" placeholder="Найти песню..." autocomplete="off">
    </div>

    <div class="search-results glass-panel" :class="{ hidden: !showResults }">
      <template v-if="isSearching">
        <div class="result-item">
          <div class="result-cover skeleton-bg"></div>
          <div class="result-info">
            <div class="skeleton-bg" style="height:14px; width:70%; margin-bottom:6px; border-radius:4px;"></div>
            <div class="skeleton-bg" style="height:10px; width:40%; border-radius:4px;"></div>
          </div>
        </div>
        <div class="result-item">
          <div class="result-cover skeleton-bg"></div>
          <div class="result-info">
            <div class="skeleton-bg" style="height:14px; width:60%; margin-bottom:6px; border-radius:4px;"></div>
            <div class="skeleton-bg" style="height:10px; width:50%; border-radius:4px;"></div>
          </div>
        </div>
      </template>
      <template v-else-if="searchResults.length === 0">
        <div class="result-item empty-result">
          <div class="result-info">
            <span class="track-title" style="color: var(--text-secondary); text-align: center;">Ничего не найдено</span>
          </div>
        </div>
      </template>
      <template v-else>
        <div
          v-for="track in searchResults"
          :key="track.id"
          class="result-item"
          :style="{
            background: localSelected?.id === track.id ? 'rgba(255, 255, 255, 0.08)' : (errorTrackId === track.id ? 'rgba(239, 68, 68, 0.15)' : '')
          }"
          @click="selectTrack(track)"
        >
          <div class="result-cover" :style="{ backgroundImage: `url(${track.cover})` }"></div>
          <div class="result-info">
            <span class="track-title">
              {{ track.title }}
              <span v-if="track.explicit" style="color: var(--status-error); font-size: 10px; margin-left: 4px;">[E]</span>
            </span>
            <span class="track-artist">{{ track.artist }}</span>
          </div>
          <svg class="check-icon" :class="{ hidden: localSelected?.id !== track.id }" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--status-success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="20 6 9 17 4 12"></polyline>
          </svg>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { OrderService } from '../services';

const emit = defineEmits(['track-selected']);

const searchQuery = ref('');
const searchResults = ref([]);
const isSearching = ref(false);
const showResults = ref(false);
const localSelected = ref(null);
const errorTrackId = ref(null);
let searchTimeout = null;

const handleInput = () => {
  localSelected.value = null;
  errorTrackId.value = null;
  emit('track-selected', null);
  clearTimeout(searchTimeout);

  if (searchQuery.value.trim().length < 2) {
    showResults.value = false;
    searchResults.value = [];
    return;
  }
  showResults.value = true;
  isSearching.value = true;

  searchTimeout = setTimeout(async () => {
    searchResults.value = await OrderService.search(searchQuery.value);
    isSearching.value = false;
  }, 500);
};

const handleFocus = () => { if (searchQuery.value.trim().length >= 2) showResults.value = true; };

const selectTrack = async (track) => {
  localSelected.value = null;
  errorTrackId.value = null;
  try {
    await OrderService.validate(track.id);
    localSelected.value = track;
    searchQuery.value = `${track.artist} — ${track.title}`;
    showResults.value = false;
    emit('track-selected', track);
  } catch (error) {
    errorTrackId.value = track.id;
    alert(error.response?.data?.detail || error.detail || "Ошибка валидации");
  }
};

const handleClickOutside = (e) => { if (!e.target.closest('.search-container')) showResults.value = false; };
onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => document.removeEventListener('click', handleClickOutside));
</script>

<style scoped>
.search-container {
  position: relative;
  width: 100%;
}

.input-wrapper {
  display: flex;
  align-items: center;
  padding: 0 16px;
  height: 52px;
  border-radius: 12px;
  transition: border-color 0.2s ease, background-color 0.2s ease;
}

.input-wrapper:focus-within {
  border-color: var(--accent-focus);
  background: var(--glass-surface-focus);
  box-shadow: 0 0 16px rgba(0, 240, 255, 0.15);
}

.search-icon {
  color: var(--text-muted);
  margin-right: 12px;
  flex-shrink: 0;
  transition: color 0.2s ease;
}

.input-wrapper:focus-within .search-icon {
  color: var(--accent-focus);
}

.input-wrapper input {
  background: none;
  border: none;
  outline: none;
  color: var(--text-primary);
  font-size: 15px;
  width: 100%;
  font-family: inherit;
}

.input-wrapper input::placeholder {
  color: var(--text-muted);
}

.search-results {
  position: absolute;
  top: calc(100% + 8px);
  left: 0;
  width: 100%;
  max-height: 250px;
  overflow-y: auto;

  /* ИСПРАВЛЕНИЕ: Поднимаем z-index и делаем жесткий плотный фон */
  z-index: 50;
  background: rgba(10, 14, 20, 0.95) !important;
  backdrop-filter: blur(24px) !important;
  -webkit-backdrop-filter: blur(24px) !important;

  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(0, 0, 0, 0.8);
}

/* Скроллбар внутри выпадающего списка */
.search-results::-webkit-scrollbar {
  width: 4px;
}
.search-results::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 4px;
}

.result-item {
  display: flex;
  align-items: center;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
}

.result-item:hover {
  background: rgba(255, 255, 255, 0.05) !important;
}

.result-item:active {
  transform: scale(0.98);
}

.empty-result {
  cursor: default;
  justify-content: center;
}
.empty-result:active {
  transform: none;
}

.result-cover {
  width: 40px;
  height: 40px;
  border-radius: 6px;
  margin-right: 12px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
}

.result-info {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.result-info .track-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.result-info .track-artist {
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 2px;
}

.check-icon {
  flex-shrink: 0;
  margin-left: 8px;
}

.hidden {
  display: none !important;
}

/* Скелетонная загрузка */
.skeleton-bg {
  background: linear-gradient(90deg, rgba(255,255,255,0.03) 25%, rgba(255,255,255,0.08) 50%, rgba(255,255,255,0.03) 75%);
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s infinite linear;
}

@keyframes skeleton-shimmer {
  to { background-position: -200% 0; }
}
</style>
