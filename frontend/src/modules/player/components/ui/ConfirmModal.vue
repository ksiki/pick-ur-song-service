<template>
  <Transition name="modal-fade">
    <div v-if="isOpen" class="modal-overlay" @click.self="cancel">
      <div class="modal-content glass-panel">
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-text">{{ message }}</p>

        <div class="modal-actions">
          <button class="btn-cancel" @click="cancel">Отмена</button>
          <button class="btn-danger" @click="confirm">Удалить</button>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { ref } from 'vue'

const isOpen = ref(false)
const title = ref('')
const message = ref('')

let resolvePromise = null

// Метод, который мы будем вызывать из других компонентов (через ref)
const show = (modalTitle, modalMessage) => {
  title.value = modalTitle
  message.value = modalMessage
  isOpen.value = true

  return new Promise((resolve) => {
    resolvePromise = resolve
  })
}

const confirm = () => {
  isOpen.value = false
  if (resolvePromise) resolvePromise(true)
}

const cancel = () => {
  isOpen.value = false
  if (resolvePromise) resolvePromise(false)
}

// Экспортируем метод show, чтобы родитель мог его дергать
defineExpose({ show })
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 90%;
  max-width: 360px;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: center;
  background: rgba(15, 20, 30, 0.95);
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.modal-text {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
}

.modal-actions {
  display: flex;
  justify-content: center;
  gap: 12px;
  margin-top: 8px;
}

button {
  padding: 10px 20px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: all 0.2s;
}

.btn-cancel {
  background: rgba(255, 255, 255, 0.05);
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-danger {
  background: rgba(239, 68, 68, 0.15);
  color: var(--status-error);
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.btn-danger:hover {
  background: var(--status-error);
  color: #fff;
}

/* Анимации модалки */
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}
.modal-fade-enter-active .modal-content,
.modal-fade-leave-active .modal-content {
  transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
.modal-fade-enter-from .modal-content {
  transform: scale(0.95) translateY(10px);
}
.modal-fade-leave-to .modal-content {
  transform: scale(0.95) translateY(10px);
}
</style>
