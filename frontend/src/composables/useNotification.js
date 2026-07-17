import { ref } from 'vue';

const isVisible = ref(false);
const notification = ref({ title: '', message: '', type: 'info' });

export function useNotification() {
  const showNotification = (title, message, type = 'info') => {
    notification.value = { title, message, type };
    isVisible.value = true;
  };

  const hideNotification = () => {
    isVisible.value = false;
  };

  return {
    isVisible,
    notification,
    showNotification,
    hideNotification
  };
}
