<template>
  <div class="order-actions">
    <div class="price-display">
      <span class="price-label">Стоимость заказа:</span>
      <span class="price-value">{{ basePrice.toFixed(2) }} BYN</span>
    </div>

    <button
      class="action-btn btn-primary"
      :disabled="!selectedTrack || isOrdering"
      @click="$emit('order', false)"
    >
      <span class="btn-text" :class="{ hidden: isOrdering && !isFast }">Заказать трек</span>
      <span class="btn-spinner" :class="{ hidden: !(isOrdering && !isFast) }"></span>
    </button>

    <button
      class="action-btn btn-secondary"
      :disabled="!selectedTrack || isOrdering"
      @click="$emit('order', true)"
    >
      <span class="btn-text" :class="{ hidden: isOrdering && isFast }">Без очереди ({{ (basePrice * 2).toFixed(2) }} BYN)</span>
      <span class="btn-spinner spinner-cyan" :class="{ hidden: !(isOrdering && isFast) }"></span>
    </button>
  </div>
</template>

<script setup>
defineProps({
  selectedTrack: Object,
  basePrice: Number,
  isOrdering: Boolean,
  isFast: Boolean
});
defineEmits(['order']);
</script>

<style scoped>
.order-actions {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-top: 12px;
}

.price-display {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px 4px;
}

.price-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
}

.price-value {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  letter-spacing: -0.5px;
}

/* Общие стили для кнопок */
.action-btn {
  position: relative;
  display: flex;
  justify-content: center;
  align-items: center;
  width: 100%;
  height: 48px;
  border-radius: 100px;
  font-size: 15px;
  font-weight: 600;
  font-family: inherit;
  cursor: pointer;
  border: none;
  transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.action-btn:active:not(:disabled) {
  transform: scale(0.97);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

/* Основная кнопка (Обычный заказ) */
.btn-primary {
  background: var(--accent-primary);
  color: #FFFFFF;
  box-shadow: 0 4px 20px rgba(255, 0, 85, 0.3);
}

.btn-primary:hover:not(:disabled) {
  background: var(--accent-hover);
  box-shadow: 0 6px 24px rgba(255, 0, 85, 0.5);
}

/* Вторичная кнопка (Fast track) */
.btn-secondary {
  background: transparent;
  color: var(--bg-glow-secondary);
  border: 1px solid var(--bg-glow-secondary);
}

.btn-secondary:hover:not(:disabled) {
  background: rgba(0, 240, 255, 0.08);
  box-shadow: 0 4px 20px rgba(0, 240, 255, 0.2);
}

/* Утилиты */
.hidden {
  display: none !important;
}

/* Спиннер загрузки */
@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.btn-spinner {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: #FFFFFF;
  animation: spin 0.8s ease-in-out infinite;
}

.spinner-cyan {
  border-color: rgba(0, 240, 255, 0.3);
  border-top-color: var(--bg-glow-secondary);
}
</style>
