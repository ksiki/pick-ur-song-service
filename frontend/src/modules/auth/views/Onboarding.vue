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
        <OnboardingForm v-if="!isSuccess" @success="isSuccess = true" />
        <OnboardingSuccess v-else @done="goToDashboard" />
      </div>
    </main>

    <footer class="app-footer">
      <p class="text-muted">© 2026 Pick Song. Для бизнеса.</p>
    </footer>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import OnboardingForm from '../components/OnboardingForm.vue';
import OnboardingSuccess from '../components/OnboardingSuccess.vue';

const router = useRouter();
const isSuccess = ref(false);

const goToDashboard = () => {
  router.push('/dashboard');
};
</script>

<style scoped src="../auth.css"></style>
