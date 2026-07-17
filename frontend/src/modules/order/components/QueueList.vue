<template>
  <section class="queue-section">
    <h2 class="section-title">Очередь ({{ queue.length }})</h2>

    <div class="queue-list">
      <article
        v-for="(track, index) in queue"
        :key="track.queueItemId || index"
        class="track-card glass-panel slide-in"
        :class="{ 'priority-track': track.isPriority }"
      >
        <div class="track-cover" :style="{ backgroundImage: `url(${track.cover})` }"></div>

        <div class="track-details">
          <div class="track-title-row">
            <h3 class="track-title">{{ track.title }}</h3>
            <span v-if="track.isPriority" class="priority-badge">Без очереди</span>
          </div>
          <p class="track-artist">{{ track.artist }}</p>
        </div>

        <div class="track-status">
          <span class="status-dot" :class="track.statusClass" :title="track.statusText"></span>
        </div>
      </article>
    </div>
  </section>
</template>

<script setup>
defineProps(['queue']);
</script>

<style scoped>
.queue-section {
  display: flex;
  flex-direction: column;
  margin-top: 8px;
}

.section-title {
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--text-secondary);
  font-weight: 600;
  margin-bottom: 12px;
}

.queue-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.track-card {
  display: flex;
  align-items: center;
  padding: 12px;
  border-radius: 12px;
  gap: 12px;
  transition: transform 0.15s ease, background-color 0.2s ease;
}

.track-card:active {
  transform: scale(0.97);
}

.track-cover {
  width: 48px;
  height: 48px;
  border-radius: 8px;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
  background-color: rgba(255, 255, 255, 0.05);
}

.track-details {
  flex-grow: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  min-width: 0;
  gap: 2px;
}

.track-title-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.track-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-artist {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.track-status {
  display: flex;
  align-items: center;
  justify-content: center;
  padding-left: 4px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

/* Статусы */
.status-dot.status-success {
  background: var(--status-success);
  box-shadow: 0 0 8px rgba(16, 185, 129, 0.4);
}

.status-dot.status-warning {
  background: var(--status-warning);
  box-shadow: 0 0 8px rgba(245, 158, 11, 0.4);
}

/* Стилизация приоритетного трека (Без очереди) */
.priority-track {
  border-color: rgba(0, 240, 255, 0.3);
  background: rgba(0, 240, 255, 0.03);
}

.priority-badge {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  padding: 2px 6px;
  border-radius: 4px;
  letter-spacing: 0.5px;
  white-space: nowrap;
  background: rgba(0, 240, 255, 0.15);
  color: var(--bg-glow-secondary);
  border: 1px solid rgba(0, 240, 255, 0.3);
}

/* Анимация появления */
.slide-in {
  animation: slide-fade-in 0.3s cubic-bezier(0.2, 0.8, 0.2, 1) forwards;
}

@keyframes slide-fade-in {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
