<template>
  <form class="auth-view active" @submit.prevent="handleOtp">
    <div class="view-header">
      <h1 class="text-primary">Код доступа</h1>
      <p class="text-secondary">
        Мы отправили 6-значный код на <br>
        <strong class="text-primary">{{ email }}</strong>
      </p>
    </div>

    <div class="input-group">
      <label for="login-otp" class="text-secondary">Код из письма</label>
      <input
        type="text"
        id="login-otp"
        v-model="form.code"
        placeholder="123456"
        minlength="6"
        maxlength="6"
        pattern="\d{6}"
        required
        autocomplete="one-time-code"
      >
    </div>

    <button type="submit" class="btn-primary" :disabled="isLoading">
      <span class="btn-text" :class="{ hidden: isLoading }">Подтвердить</span>
      <span class="btn-spinner" :class="{ hidden: !isLoading }"></span>
    </button>

    <div class="view-footer">
      <a href="#" @click.prevent="$emit('back')" class="text-secondary" style="text-decoration: underline; text-underline-offset: 4px;">
        Вернуться назад
      </a>
    </div>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { AuthService } from '../services';

const props = defineProps({ email: String });
const emit = defineEmits(['back']);
const router = useRouter();

const isLoading = ref(false);
const form = reactive({ code: '' });

const handleOtp = async () => {
  isLoading.value = true;
  try {
    await AuthService.verifyLoginOtp(props.email, form.code);
    router.push('/dashboard');
  } catch (error) {
    alert(`Ошибка: ${error.response?.data?.detail || 'Неверный код подтверждения'}`);
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped src="../auth.css"></style>
