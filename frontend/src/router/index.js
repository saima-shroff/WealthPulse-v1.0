import { createRouter, createWebHistory } from 'vue-router'
import { currentUser } from '../services/api'
import AppShell from '../components/AppShell.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import DashboardView from '../views/DashboardView.vue'
import TransactionsView from '../views/TransactionsView.vue'
import AccountsView from '../views/AccountsView.vue'
import BudgetsView from '../views/BudgetsView.vue'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: LoginView, meta: { guest: true } },
    { path: '/register', component: RegisterView, meta: { guest: true } },
    {
      path: '/',
      component: AppShell,
      meta: { requiresAuth: true },
      children: [
        { path: '', component: DashboardView },
        { path: 'transactions', component: TransactionsView },
        { path: 'accounts', component: AccountsView },
        { path: 'budgets', component: BudgetsView },
      ],
    },
  ],
})

router.beforeEach((to) => {
  if (to.meta.requiresAuth && !localStorage.getItem('wealthpulse-token')) return '/login'
  if (to.meta.guest && localStorage.getItem('wealthpulse-token')) return '/'
})

export default router