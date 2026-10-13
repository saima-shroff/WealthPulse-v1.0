<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Activity, ArrowDownLeft, ArrowUpRight, ChartNoAxesCombined, CircleUserRound, LayoutDashboard, LogOut, WalletCards } from 'lucide-vue-next'
import { clearSession, currentUser } from '../services/api'

const route = useRoute()
const router = useRouter()
const user = currentUser()
const firstName = computed(() => user?.email?.split('@')[0] || 'there')
const pageTitles = {
  '/': ['Your overview'],
  '/transactions': ['Transactions', 'YOUR MONEY, IN MOTION'],
  '/accounts': ['Accounts', 'WHERE YOUR MONEY LIVES'],
  '/budgets': ['Budgets', 'A PLAN FOR EVERY CATEGORY'],
}
const pageTitle = computed(() => {
  const title = pageTitles[route.path] || pageTitles['/']
  const today = new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }).toUpperCase()
  return [title[0], title[1] || today]
})

function signOut() {
  clearSession()
  router.replace('/login')
}
</script>

<template>
  <div class="app-frame">
    <aside class="sidebar">
      <RouterLink class="brand" to="/">
        <span class="brand-mark"><Activity :size="19" :stroke-width="2.5" /></span>
        <span>wealth<span class="brand-light">pulse</span></span>
      </RouterLink>
      <div class="side-label">WORKSPACE</div>
      <nav class="side-nav" aria-label="Main navigation">
        <RouterLink to="/" class="nav-link"><LayoutDashboard :size="18" />Overview</RouterLink>
        <RouterLink to="/transactions" class="nav-link"><ArrowDownLeft :size="18" />Transactions</RouterLink>
        <RouterLink to="/accounts" class="nav-link"><WalletCards :size="18" />Accounts</RouterLink>
        <RouterLink to="/budgets" class="nav-link"><ChartNoAxesCombined :size="18" />Budgets</RouterLink>
      </nav>
      <div class="sidebar-bottom">
        <div class="side-label">YOUR PROFILE</div>
        <div class="profile-chip">
          <span class="profile-avatar"><CircleUserRound :size="20" /></span>
          <span class="profile-name">{{ firstName }}</span>
          <button class="icon-button logout-button" title="Sign out" aria-label="Sign out" @click="signOut"><LogOut :size="17" /></button>
        </div>
        <div class="sidebar-footnote"><span class="status-dot"></span> Private &amp; secure</div>
      </div>
    </aside>

    <main class="main-area">
      <header class="topbar">
        <div class="breadcrumb"><span>Workspace</span><span class="crumb-slash">/</span><strong>{{ pageTitle[0] }}</strong></div>
        <div class="topbar-right"><span class="date-label">{{ pageTitle[1] }}</span><span class="top-avatar">{{ firstName.slice(0, 1).toUpperCase() }}</span></div>
      </header>
      <section class="view-area"><RouterView /></section>
    </main>

    <nav class="mobile-nav" aria-label="Mobile navigation">
      <RouterLink to="/" title="Overview"><LayoutDashboard :size="20" /></RouterLink>
      <RouterLink to="/transactions" title="Transactions"><ArrowDownLeft :size="20" /></RouterLink>
      <RouterLink to="/accounts" title="Accounts"><WalletCards :size="20" /></RouterLink>
      <RouterLink to="/budgets" title="Budgets"><ChartNoAxesCombined :size="20" /></RouterLink>
      <button title="Sign out" aria-label="Sign out" @click="signOut"><LogOut :size="20" /></button>
    </nav>
  </div>
</template>