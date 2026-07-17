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
      <div class="glass-panel">
        <LoginForm v-if="step === 1" @success="handleLoginSuccess" />
        <OtpForm v-else :email="userEmail" @back="step = 1" />
      </div>
    </main>

    <footer class="app-footer">
      <p class="text-muted">© 2026 Pick Song. Для бизнеса.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import LoginForm from '../components/LoginForm.vue';
import OtpForm from '../components/OtpForm.vue';

const step = ref(1);
const userEmail = ref('');

const handleLoginSuccess = (email) => {
  userEmail.value = email;
  step.value = 2;
};
</script>

<style scoped src="../auth.css"></style>
