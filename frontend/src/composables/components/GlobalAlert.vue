<template>
  <Teleport to="body">
    <Transition name="toast-fade">
      <div v-if="isVisible" class="global-alert-wrapper">
        <div class="glass-panel alert-card" :class="`alert-${notification.type}`">

          <div class="alert-icon">
            <svg v-if="notification.type === 'success'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--status-success)" stroke-width="2">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <svg v-else-if="notification.type === 'info'" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--accent-focus)" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line>
            </svg>
            <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="var(--status-error)" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line>
            </svg>
          </div>

          <div class="alert-content">
            <h4 class="alert-title">{{ notification.title }}</h4>
            <p class="alert-message">{{ notification.message }}</p>
          </div>

          <button class="alert-ok-btn" @click="hideNotification">ОК</button>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue';
import { useNotification } from '../useNotification';

const { isVisible, notification, hideNotification } = useNotification();

let mouseListener = null;

// Следим за появлением уведомления
watch(isVisible, (newValue) => {
  if (newValue) {
    // Даем 1.5 секунды иммунитета, чтобы человек успел прочитать,
    // прежде чем движение мыши закроет окно.
    setTimeout(() => {
      if (isVisible.value) {
        mouseListener = () => {
          hideNotification();
          window.removeEventListener('mousemove', mouseListener);
        };
        window.addEventListener('mousemove', mouseListener);
      }
    }, 1500);
  } else {
    // Очищаем слушатель, если закрыли по кнопке
    if (mouseListener) {
      window.removeEventListener('mousemove', mouseListener);
      mouseListener = null;
    }
  }
});
</script>

<style scoped>
.global-alert-wrapper {
  position: fixed;
  top: 24px;
  left: 50%;
  transform: translateX(-50%);
  z-index: 9999; /* Поверх всего */
  width: 90%;
  max-width: 400px;
  pointer-events: none; /* Чтобы мышь проходила сквозь обертку */
}

.alert-card {
  pointer-events: auto; /* Возвращаем события для самой карточки */
  display: flex;
  align-items: center;
  padding: 16px;
  gap: 16px;
  background: rgba(15, 20, 30, 0.95);
  border-left: 4px solid var(--glass-border);
}

.alert-success { border-left-color: var(--status-success); }
.alert-error { border-left-color: var(--status-error); }
.alert-info { border-left-color: var(--accent-focus); }

.alert-icon {
  flex-shrink: 0;
  display: flex;
}

.alert-content {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.alert-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

.alert-message {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.4;
}

.alert-ok-btn {
  background: rgba(255, 255, 255, 0.1);
  color: var(--text-primary);
  border: none;
  padding: 8px 16px;
  border-radius: 100px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.alert-ok-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* Анимация появления сверху */
.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
}
.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -20px);
}
</style>
