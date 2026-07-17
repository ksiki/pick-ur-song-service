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

    <main class="main-container">
      <div class="glass-panel center-text">

        <div v-if="isLoading" class="auth-view active">
          <h1 class="text-primary">Проверка данных...</h1>
          <p class="text-secondary">Пожалуйста, подождите, мы проверяем вашу ссылку.</p>
          <div style="display: flex; justify-content: center; margin-top: 24px; min-height: 40px; position: relative;">
              <span class="btn-spinner" style="border-top-color: var(--accent-primary);"></span>
          </div>
        </div>

        <div v-else-if="error" class="auth-view active">
          <svg class="status-icon" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="var(--status-error)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <h1 class="text-primary" style="color: var(--status-error)">Ошибка верификации</h1>
          <p class="text-secondary">{{ error }}</p>
          <button @click="goToLogin" class="btn-primary mt-medium">На страницу входа</button>
        </div>

      </div>
    </main>

    <footer class="app-footer">
      <p class="text-muted">© 2026 Pick Song. Для бизнеса.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { AuthService } from '../services'; // Твой сервис

const route = useRoute();
const router = useRouter();

const isLoading = ref(true);
const error = ref(null);

onMounted(async () => {
  // Вытаскиваем ?token=... из адресной строки
  const token = route.query.token;

  if (!token) {
    error.value = 'Токен не найден в ссылке. Пожалуйста, скопируйте ссылку из письма полностью.';
    isLoading.value = false;
    return;
  }

  try {
    // Отправляем токен на бэкенд для верификации
    await AuthService.verify(token);

    // ЕСЛИ УСПЕШНО: сразу перебрасываем на Шаг 2 (Онбординг)
    router.push('/auth/onboarding');
  } catch (err) {
    error.value = err.response?.data?.detail || 'Неверный или устаревший токен. Попробуйте зарегистрироваться заново.';
  } finally {
    isLoading.value = false;
  }
});

const goToLogin = () => {
  router.push('/login');
};
</script>

<style scoped src="../auth.css"></style>
