<template>
  <form class="auth-view active" @submit.prevent="handleRegister">
    <div class="view-header">
      <h1 class="text-primary">Регистрация</h1>
      <p class="text-secondary">Шаг 1 из 2: Базовые данные</p>
    </div>

    <div class="input-group">
      <label for="reg-email" class="text-secondary">Рабочий Email</label>
      <input
        type="email"
        id="reg-email"
        v-model="form.email"
        placeholder="hello@venue.com" required
        autocomplete="email"
      >
    </div>

    <div class="input-group">
      <label for="reg-password" class="text-secondary">Пароль (минимум 8 символов)</label>
      <input
        type="password"
        id="reg-password"
        v-model="form.password"
        placeholder="••••••••"
        minlength="8"
        required
        autocomplete="new-password"
      >
    </div>

    <button type="submit" class="btn-primary" :disabled="isLoading">
      <span class="btn-text" :class="{ hidden: isLoading }">Продолжить</span>
      <span class="btn-spinner" :class="{ hidden: !isLoading }"></span>
    </button>

    <div class="view-footer text-secondary">
      Уже есть аккаунт? <router-link to="/auth/login" class="text-accent">Войти</router-link>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { AuthService } from '../services';

const emit = defineEmits(['success']);
const isLoading = ref(false);

const form = reactive({
  email: '',
  password: ''
});

const handleRegister = async () => {
  isLoading.value = true;
  try {
    await AuthService.register(form.email, form.password);
    emit('success');
  } catch (error) {
    const detail = error.response?.data?.detail;
    const errMsg = Array.isArray(detail) ? detail[0].msg : (detail || 'Ошибка регистрации');
    alert(`Ошибка: ${errMsg}`);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped src="../auth.css"></style>
