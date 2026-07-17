<template>
  <form class="auth-view active" @submit.prevent="handleLogin">
    <div class="view-header">
      <h1 class="text-primary">Вход в систему</h1>
      <p class="text-secondary">Управляйте очередью вашего заведения</p>
    </div>

    <div class="input-group">
      <label for="login-email" class="text-secondary">Email</label>
      <input
        type="email"
        id="login-email"
        v-model="form.email"
        placeholder="venue@example.com" required
        autocomplete="email"
      >
    </div>

    <div class="input-group">
      <label for="login-password" class="text-secondary">Пароль</label>
      <input
        type="password"
        id="login-password"
        v-model="form.password"
        placeholder="••••••••"
        required
        autocomplete="current-password"
      >
    </div>

    <button type="submit" class="btn-primary" :disabled="isLoading">
      <span class="btn-text" :class="{ hidden: isLoading }">Войти</span>
      <span class="btn-spinner" :class="{ hidden: !isLoading }"></span>
    </button>

    <div class="view-footer text-secondary">
      Нет аккаунта? <router-link to="/auth/register" class="text-accent">Создать заведение</router-link>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { AuthService } from '../services';

const emit = defineEmits(['success']);
const isLoading = ref(false);
const form = reactive({ email: '', password: '' });

const handleLogin = async () => {
  isLoading.value = true;
  try {
    await AuthService.login(form.email, form.password);
    emit('success', form.email);
  } catch (error) {
    const detail = error.response?.data?.detail;
    if (Array.isArray(detail)) {
      const messages = detail.map(err => `Поле "${err.loc.at(-1)}": ${err.msg}`).join('\n');
      alert(`Ошибка валидации:\n${messages}`);
    } else {
      alert(`Ошибка: ${detail || 'Неверный код'}`);
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped src="../auth.css"></style>
