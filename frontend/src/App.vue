<template>
  <div class="bg-layer">
    <!-- <div class="glow-spot primary-glow"></div>
    <div class="glow-spot secondary-glow"></div> -->
  </div>

  <div :class="{ 'app-wrapper': route.name !== 'Player' }">
    <router-view></router-view>
  </div>

  <GlobalAlert />
</template>

<script setup>
import { useRoute } from 'vue-router'
import GlobalAlert from './composables/components/GlobalAlert.vue'

const route = useRoute()
</script>
