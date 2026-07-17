<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div class="modal-overlay" @click.self="$emit('close')">
        <div class="modal-content glass-panel">

          <button class="close-btn" aria-label="Закрыть" @click="$emit('close')">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <h2 class="modal-title">Выберите заведение</h2>

          <div class="bars-list">
            <div
              v-for="bar in bars"
              :key="bar.id"
              class="bar-card"
              :class="{ 'is-active': selectedBarId === bar.id }"
              @click="selectedBarId = bar.id"
            >
              <div class="bar-info">
                <span class="bar-name">{{ bar.name }}</span>
                <span class="bar-address" v-if="bar.address">{{ bar.address }}</span>
              </div>

              <div class="radio-indicator">
                <div class="radio-dot"></div>
              </div>
            </div>
          </div>

          <button
            class="btn-primary mt-medium"
            :disabled="!selectedBarId || isRedirecting"
            @click="proceedToPlayer"
          >
            {{ isRedirecting ? 'Подключение...' : 'Перейти к Плееру' }}
          </button>

        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { MenuService } from '../services.js';

// Принимаем массив заведений от родителя (Menu.vue)
const props = defineProps({
  bars: {
    type: Array,
    required: true,
    default: () => []
  }
});

const emit = defineEmits(['close']);

const selectedBarId = ref(null);
const isRedirecting = ref(false);

onMounted(() => {
  // Читаем последний выбор из localStorage
  const savedBarId = localStorage.getItem('lastSelectedBarId');
  if (savedBarId && props.bars.length > 0) {
    const barExists = props.bars.some(bar => bar.id === savedBarId);
    if (barExists) {
      selectedBarId.value = savedBarId;
    } else {
      localStorage.removeItem('lastSelectedBarId');
    }
  }
});

const proceedToPlayer = async () => {
  if (!selectedBarId.value) return;

  isRedirecting.value = true;
  try {
    localStorage.setItem('lastSelectedBarId', selectedBarId.value);

    const response = await MenuService.getPlayerUrl(selectedBarId.value);
    window.location.href = response.url;
  } catch (error) {
    console.error('Ошибка при генерации ссылки:', error);
    isRedirecting.value = false;
  }
};
</script>

<style scoped>
/* Все твои стили для модалки остаются абсолютно без изменений */
.modal-overlay { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; background: rgba(0, 0, 0, 0.7); backdrop-filter: blur(4px); -webkit-backdrop-filter: blur(4px); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 16px; }
.modal-content { width: 100%; max-width: 400px; padding: 24px; position: relative; background: rgba(15, 20, 30, 0.95); display: flex; flex-direction: column; }
.close-btn { position: absolute; top: 16px; right: 16px; background: transparent; border: none; color: var(--text-secondary); cursor: pointer; transition: color 0.2s ease, transform 0.1s ease; display: flex; align-items: center; justify-content: center; padding: 4px; }
.close-btn:hover { color: var(--text-primary); }
.close-btn:active { transform: scale(0.9); }
.modal-title { font-size: 20px; font-weight: 600; margin-bottom: 20px; color: var(--text-primary); text-align: center; }
.bars-list { display: flex; flex-direction: column; gap: 12px; max-height: 320px; overflow-y: auto; padding-right: 4px; }
.bars-list::-webkit-scrollbar { width: 4px; }
.bars-list::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }
.bar-card { display: flex; justify-content: space-between; align-items: center; padding: 16px; background: rgba(255, 255, 255, 0.03); border: 1px solid var(--glass-border); border-radius: 12px; cursor: pointer; transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1); }
.bar-card:hover { background: rgba(255, 255, 255, 0.06); }
.bar-card:active { transform: scale(0.98); }
.bar-info { display: flex; flex-direction: column; gap: 4px; }
.bar-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.bar-address { font-size: 13px; color: var(--text-secondary); }
.radio-indicator { width: 20px; height: 20px; border-radius: 50%; border: 2px solid var(--text-secondary); display: flex; align-items: center; justify-content: center; transition: border-color 0.2s ease; flex-shrink: 0; }
.radio-dot { width: 10px; height: 10px; border-radius: 50%; background: transparent; transition: background-color 0.2s ease, transform 0.2s cubic-bezier(0.4, 0, 0.2, 1); transform: scale(0); }
.bar-card.is-active { background: rgba(0, 240, 255, 0.05); border-color: var(--bg-glow-secondary); box-shadow: 0 4px 16px rgba(0, 240, 255, 0.1); }
.bar-card.is-active .radio-indicator { border-color: var(--bg-glow-secondary); }
.bar-card.is-active .radio-dot { background: var(--bg-glow-secondary); transform: scale(1); }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-active .modal-content, .modal-fade-leave-active .modal-content { transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .modal-content, .modal-fade-leave-to .modal-content { transform: scale(0.95) translateY(10px); }
</style>
