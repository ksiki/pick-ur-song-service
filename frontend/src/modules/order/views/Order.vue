<template>
  <div class="dashboard-wrapper">
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

    <main class="main-content">
      <section class="bar-info glass-panel">
        <div class="bar-header">
          <h1 class="bar-name">{{ venueName }}</h1>
          <span class="status-badge status-open">Открыто</span>
        </div>
        <div class="bar-details">
          <span class="working-hours">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="10"></circle>
              <polyline points="12 6 12 12 16 14"></polyline>
            </svg>
            Сегодня до 04:00
          </span>
          <span class="venue-address" v-if="venueAddress">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path>
              <circle cx="12" cy="10" r="3"></circle>
            </svg>
            {{ venueAddress }}
          </span>
        </div>
      </section>

      <section class="order-section">
        <TrackSearch @track-selected="track => selectedTrack = track" />

        <OrderActions
          :selectedTrack="selectedTrack"
          :basePrice="basePrice"
          :isOrdering="isOrdering"
          :isFast="isFastTrackOrdering"
          @order="handleOrder"
        />
      </section>

      <QueueList :queue="queue" />
    </main>

    <PaymentModal
      v-if="showPaymentModal"
      :track="selectedTrack"
      @close="showPaymentModal = false"
      @pay="simulatePayment"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import TrackSearch from '../components/TrackSearch.vue';
import OrderActions from '../components/OrderActions.vue';
import QueueList from '../components/QueueList.vue';
import PaymentModal from '../components/PaymentModal.vue';

const selectedTrack = ref(null);
const basePrice = ref(3.50);
const isOrdering = ref(false);
const isFastTrackOrdering = ref(false);
const pendingOrderType = ref('standard');
const showPaymentModal = ref(false);

const venueName = ref('Загрузка...');
const venueAddress = ref('');

const queue = ref([
  {
    id: 'mock-1',
    title: 'Midnight City',
    artist: 'M83',
    statusClass: 'status-success',
    statusText: 'В очереди'
  }
]);

onMounted(() => {
  // Чтение параметров из URL
  const urlParams = new URLSearchParams(window.location.search);
  const venueFromUrl = urlParams.get('venue');
  const addressFromUrl = urlParams.get('address');

  if (venueFromUrl) {
    const decodedVenue = decodeURIComponent(venueFromUrl);
    localStorage.setItem('guest_venue_name', decodedVenue);
    venueName.value = decodedVenue;
  } else {
    venueName.value = localStorage.getItem('guest_venue_name') || 'Neon Lounge Bar';
  }

  if (addressFromUrl) {
    const decodedAddress = decodeURIComponent(addressFromUrl);
    localStorage.setItem('guest_venue_address', decodedAddress);
    venueAddress.value = decodedAddress;
  } else {
    venueAddress.value = localStorage.getItem('guest_venue_address') || '';
  }

  // Очистка URL
  if (venueFromUrl || addressFromUrl) {
    const newUrl = window.location.origin + window.location.pathname;
    window.history.replaceState({}, document.title, newUrl);
  }
});

const handleOrder = (isFast) => {
  isOrdering.value = true;
  isFastTrackOrdering.value = isFast;
  pendingOrderType.value = isFast ? 'priority' : 'standard';

  setTimeout(() => {
    isOrdering.value = false;
    showPaymentModal.value = true;
  }, 600);
};

const simulatePayment = () => {
  showPaymentModal.value = false;
  const isPriority = pendingOrderType.value === 'priority';

  const newTrack = {
    ...selectedTrack.value,
    queueItemId: Date.now().toString(),
    statusClass: 'status-warning',
    statusText: 'В обработке',
    isPriority: isPriority
  };

  if (isPriority) {
    const firstStandardIndex = queue.value.findIndex(t => !t.isPriority);
    firstStandardIndex !== -1 ? queue.value.splice(firstStandardIndex, 0, newTrack) : queue.value.push(newTrack);
  } else {
    queue.value.push(newTrack);
  }

  setTimeout(() => {
    const trackInQueue = queue.value.find(t => t.queueItemId === newTrack.queueItemId);
    if (trackInQueue) {
      trackInQueue.statusClass = 'status-success';
      trackInQueue.statusText = 'Оплачено';
    }
  }, 3000);

  selectedTrack.value = null;
  isFastTrackOrdering.value = false;
};
</script>

<style scoped>
.dashboard-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.app-header {
  display: flex;
  justify-content: center;
  padding-top: 8px;
  padding-bottom: 32px;
}

.logo-container {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-text {
  font-size: 24px;
  font-weight: 600;
  letter-spacing: -0.5px;
  background: linear-gradient(90deg, #FFFFFF, #94A3B8);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.main-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.bar-info {
  padding: 18px 20px;
  border-radius: 16px;
  transition: border-color 0.3s ease;
}

.bar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.bar-name {
  font-size: 20px;
  font-weight: 600;
  letter-spacing: -0.3px;
  color: var(--text-primary);
}

.status-badge {
  font-size: 11px;
  font-weight: 600;
  padding: 4px 12px;
  border-radius: 100px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.status-open {
  background: rgba(16, 185, 129, 0.12);
  color: var(--status-success);
  border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Изменено для поддержки нескольких строк (время и адрес) */
.bar-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.working-hours, .venue-address {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 400;
}

.working-hours svg, .venue-address svg {
  color: var(--accent-primary);
  flex-shrink: 0;
}
</style>
