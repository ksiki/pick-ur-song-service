<template>
  <Teleport to="body">
    <Transition name="modal-fade" appear>
      <div class="modal-overlay" id="payment-modal" @click.self="$emit('close')">
        <div class="modal-content glass-panel">
          <button class="close-btn" aria-label="Закрыть" @click="$emit('close')">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="18" y1="6" x2="6" y2="18"></line>
              <line x1="6" y1="6" x2="18" y2="18"></line>
            </svg>
          </button>

          <h2 class="modal-title">Оплата заказа</h2>

          <div class="selected-track-preview">
            <div v-if="track" class="track-card">
              <div class="track-cover" :style="{ backgroundImage: `url(${track.cover})` }"></div>
              <div class="track-details">
                <h3 class="track-title">{{ track.title }}</h3>
                <p class="track-artist">{{ track.artist }}</p>
              </div>
            </div>
          </div>

          <div class="payment-placeholder">
            <p class="placeholder-text">Форма эквайринга</p>
            <button class="btn-primary" @click="$emit('pay')">Оплатить (Симуляция)</button>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
defineProps({
  track: Object
});

defineEmits(['close', 'pay']);
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
  -webkit-backdrop-filter: blur(4px);
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
}

.modal-content {
  width: 100%;
  max-width: 400px;
  padding: 24px;
  position: relative;
  background: rgba(15, 20, 30, 0.95);
  display: flex;
  flex-direction: column;
  text-align: center;
}

.close-btn {
  position: absolute;
  top: 16px;
  right: 16px;
  background: transparent;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  transition: color 0.2s ease, transform 0.1s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 4px;
}

.close-btn:hover {
  color: var(--text-primary);
}

.close-btn:active {
  transform: scale(0.9);
}

.modal-title {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 20px;
  color: var(--text-primary);
}

.selected-track-preview {
  margin-bottom: 24px;
}

.track-card {
  display: flex;
  align-items: center;
  padding: 12px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  text-align: left;
}

.track-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  margin-right: 16px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
  background-color: rgba(255, 255, 255, 0.05);
}

.track-details {
  flex-grow: 1;
  overflow: hidden;
}

.track-details .track-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  margin-bottom: 4px;
}

.track-details .track-artist {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.payment-placeholder {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.placeholder-text {
  font-size: 13px;
  color: var(--text-secondary);
}

.btn-primary {
  background: var(--accent-primary);
  color: #FFFFFF;
  border: none;
  border-radius: 100px;
  padding: 0 24px;
  height: 48px;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  width: 100%;
  box-shadow: 0 4px 20px rgba(255, 0, 85, 0.3);
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.btn-primary:hover {
  background: var(--accent-hover);
  box-shadow: 0 6px 24px rgba(255, 0, 85, 0.5);
}

.btn-primary:active {
  transform: scale(0.97);
}

/* Анимации модального окна */
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

.modal-fade-enter-from .modal-content,
.modal-fade-leave-to .modal-content {
  transform: scale(0.95) translateY(10px);
}
</style>
