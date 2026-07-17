<template>
  <form class="auth-view active" @submit.prevent="handleOnboarding">
    <div class="view-header">
      <h1 class="text-primary">Активация профиля</h1>
      <p class="text-secondary">Шаг 2 из 2: Юридическая информация</p>
    </div>

    <div class="input-group">
      <label for="ob-name" class="text-secondary">Коммерческое название (видят гости)</label>
      <input
        type="text"
        id="ob-name"
        v-model="form.venue_name"
        placeholder="Например: Neon Club"
        maxlength="255"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-legal-name" class="text-secondary">Юридическое лицо</label>
      <input
        type="text"
        id="ob-legal-name"
        v-model="form.legal_name"
        placeholder="ООО 'Неон Бар'"
        maxlength="255"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-unp" class="text-secondary">УНП (строго 9 цифр)</label>
      <input
        type="text"
        id="ob-unp"
        v-model="form.unp"
        placeholder="123456789"
        minlength="9"
        maxlength="9"
        pattern="\d{9}"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-iban" class="text-secondary">Расчетный счет (IBAN)</label>
      <input
        type="text"
        id="ob-iban"
        v-model="form.iban"
        placeholder="BY00XXXX00000000000000000000"
        minlength="28"
        maxlength="28"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-country" class="text-secondary">Страна</label>
      <input
        type="text"
        id="ob-country"
        v-model="form.country"
        placeholder="Например: Беларусь"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-city" class="text-secondary">Город</label>
      <input
        type="text"
        id="ob-city"
        v-model="form.city"
        placeholder="Например: Гомель"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-street" class="text-secondary">Улица</label>
      <input
        type="text"
        id="ob-street"
        v-model="form.street"
        placeholder="Например: Советская"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-house" class="text-secondary">Дом / Строение</label>
      <input
        type="text"
        id="ob-house"
        v-model="form.house"
        placeholder="Например: 34"
        required
      >
    </div>
    <div class="input-group">
      <label for="ob-phone" class="text-secondary">Контактный телефон</label>
      <input
        type="tel"
        id="ob-phone"
        v-model="form.venue_number"
        @input="enforcePhoneFormat"
        placeholder="+375291234567"
        required
      >
    </div>

    <div class="input-group">
      <label for="ob-code-phrase" class="text-secondary">Кодовая фраза (от 8 до 64 символов)</label>
      <input
        type="text"
        id="ob-code-phrase"
        v-model="form.admin_passcode"
        placeholder="Введите секретную фразу"
        minlength="8"
        maxlength="64"
        required
      >
    </div>

    <button type="submit" class="btn-primary" :disabled="isLoading">
      <span class="btn-text" :class="{ hidden: isLoading }">Сохранить и активировать</span>
      <span class="btn-spinner" :class="{ hidden: !isLoading }"></span>
    </button>
  </form>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { AuthService } from '../services';

const emit = defineEmits(['success']);
const isLoading = ref(false);

const form = reactive({
  venue_name: '',
  legal_name: '',
  unp: '',
  iban: '',
  admin_passcode: '',
  venue_number: '+',
  country: 'Беларусь', // Можно оставить пустым, если хочется
  city: '',
  street: '',
  house: ''
});

const enforcePhoneFormat = () => {
  const digitsOnly = form.venue_number.replace(/[^0-9]/g, '');
  form.venue_number = '+' + digitsOnly;
};

const handleOnboarding = async () => {
  isLoading.value = true;
  try {
    // Склеиваем адрес перед отправкой и собираем нужный payload
    const payload = {
      legal_name: form.legal_name,
      unp: form.unp,
      iban: form.iban,
      venue_name: form.venue_name,
      venue_number: form.venue_number,
      address: `${form.country}, ${form.city}, ${form.street}, ${form.house}`,
      admin_passcode: form.admin_passcode
    };

    await AuthService.onboarding(payload);
    emit('success');
  } catch (error) {
    const detail = error.response?.data?.detail;
    if (Array.isArray(detail)) {
      const messages = detail.map(err => `Поле ${err.loc.at(-1)}: ${err.msg}`).join('\n');
      alert(`Ошибка заполнения:\n${messages}`);
    } else {
      alert(`Ошибка: ${detail || 'Ошибка сохранения данных'}`);
    }
  } finally {
    isLoading.value = false;
  }
};
</script>

<style scoped src="../auth.css"></style>
