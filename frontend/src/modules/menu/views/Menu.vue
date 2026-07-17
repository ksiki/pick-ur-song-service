<template>
  <div class="app-wrapper">
    <header class="app-header">
      <div class="logo-container">
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
          <path d="M9 18V5L21 3V16" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="6" cy="18" r="3" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          <circle cx="18" cy="16" r="3" stroke="var(--accent-primary, #FF0055)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <span class="logo-text">Pick Song</span>
      </div>
    </header>

    <main class="main-container menu-content">
      <div class="glass-panel menu-panel">
        <h1 class="text-primary title">Добро пожаловать</h1>

        <template v-if="isLoading">
          <p class="text-secondary subtitle">Загружаем ваши заведения...</p>
        </template>

        <template v-else-if="bars.length === 0">
          <p class="text-secondary subtitle">У вас пока нет активных заведений.</p>
          <div class="action-buttons">
            <button class="btn-primary" @click="createBar">
              Добавить заведение
            </button>
            <button class="btn-glass" @click="goToAdmin">
              Админ панель
            </button>
          </div>
        </template>

        <template v-else>
          <p class="text-secondary subtitle">Выберите раздел для работы</p>
          <div class="action-buttons">
            <button class="btn-primary" @click="openPlayerSelection">
              Перейти к Плееру
            </button>
            <button class="btn-glass" @click="goToAdmin">
              Админ панель
            </button>
          </div>
        </template>
      </div>
    </main>

    <BarSelectModal
      v-if="showBarModal"
      :bars="bars"
      @close="showBarModal = false"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import BarSelectModal from '../components/BarSelectModal.vue';
import { MenuService } from '../services.js';

const router = useRouter();
const showBarModal = ref(false);
const isLoading = ref(true);
const bars = ref([]);

onMounted(async () => {
  try {
    const data = await MenuService.getVenues();
    bars.value = Array.isArray(data) ? data : (data.venues || []);
  } catch (error) {
    console.error('Ошибка при загрузке заведений:', error);
  } finally {
    isLoading.value = false;
  }
});

const openPlayerSelection = () => {
  showBarModal.value = true;
};

const createBar = () => {
  // Заглушка. Оставляем пользователя на этой странице, как ты и просил.
  // В будущем здесь можно открыть модалку создания заведения.
  console.log('Открытие формы создания заведения...');
};

const goToAdmin = () => {
  console.log('Переход в админ панель...');
};
</script>

<style scoped>
/* Твои текущие стили без изменений */
.main-container {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.menu-panel {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 40px 24px;
  text-align: center;
}

.title {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 8px;
}

.subtitle {
  font-size: 14px;
  margin-bottom: 32px;
}

.action-buttons {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.btn-glass {
  width: 100%;
  height: 48px;
  background: transparent;
  color: var(--text-primary);
  border: 1px solid var(--glass-border);
  border-radius: 100px;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
  display: flex;
  justify-content: center;
  align-items: center;
}

.btn-glass:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.15);
}

.btn-glass:active {
  transform: scale(0.97);
}
</style>
