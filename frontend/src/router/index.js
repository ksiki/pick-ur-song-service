import { createRouter, createWebHistory } from 'vue-router'
import Login from '../modules/auth/views/Login.vue'
import Register from '../modules/auth/views/Register.vue'
import Verify from '../modules/auth/views/Verify.vue';
import Onboarding from '../modules/auth/views/Onboarding.vue'
import Order from '../modules/order/views/Order.vue'
import Player from '../modules/player/views/Player.vue'
import Menu from '../modules/menu/views/Menu.vue'

const routes = [
  {
    path: '/auth/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/auth/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/auth/verify',
    name: 'Verify',
    component: Verify
  },
  {
    path: '/auth/onboarding',
    name: 'Onboarding',
    component: Onboarding
  },
  {
    path: '/order/:bar_id',
    name: 'Order',
    component: Order
  },
  {
    path: '/menu',
    name: 'Menu',
    component: Menu,
    meta: { requiresAuth: true }
  },
  {
    path: '/player',
    name: 'Player',
    component: Player,
    meta: { requiresPlayerAuth: true }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/auth/login'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})


router.beforeEach((to, from, next) => {
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth);
  const requiresPlayerAuth = to.matched.some(record => record.meta.requiresPlayerAuth);

  const isAuthenticated = !!localStorage.getItem('is_logged_in');

  const hasPlayerToken = !!to.query.token || !!localStorage.getItem('player_iframe_token');

  if (requiresAuth && !isAuthenticated) {
    next({ path: '/auth/login', query: { redirect: to.fullPath } });
  } else if ((to.path === '/auth/login' || to.path === '/auth/register') && isAuthenticated) {
    next('/menu');
  }
  else if (requiresPlayerAuth && !hasPlayerToken) {
    console.error('Отсутствует токен доступа к плееру');
    next(false);
  }
  else {
    next();
  }
});

export default router
