<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Activity, ArrowRight, LockKeyhole } from 'lucide-vue-next'
import { api, errorMessage, setSession } from '../services/api'

const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function submit() {
  error.value = ''
  loading.value = true
  try {
    const { data } = await api.post('/auth/login', { email: email.value, password: password.value })
    setSession(data.user, data.token)
    router.replace('/')
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-art">
      <RouterLink class="brand auth-brand" to="/login"><span class="brand-mark"><Activity :size="19" :stroke-width="2.5" /></span><span>wealth<span class="brand-light">pulse</span></span></RouterLink>
      <div class="auth-quote"><span class="eyebrow">MONEY, WITH A LITTLE MORE CLARITY</span><h1>Feel good<br />about where<br /><em>you're going.</em></h1><div class="auth-orbit"><span></span><span></span><span></span><div class="orbit-center"><ArrowRight :size="25" /></div></div></div>
      <div class="auth-art-footer">A calmer relationship with your money.</div>
    </section>
    <section class="auth-form-side">
      <div class="auth-form-wrap">
        <div class="auth-form-icon"><LockKeyhole :size="19" /></div>
        <div class="eyebrow">WELCOME BACK</div>
        <h2>Sign in to WealthPulse</h2>
        <p class="auth-subtitle">Your financial picture, right where you left it.</p>
        <form class="form-stack" @submit.prevent="submit">
          <label>Email address<input v-model.trim="email" type="email" autocomplete="email" placeholder="you@example.com" required /></label>
          <label>Password<input v-model="password" type="password" autocomplete="current-password" placeholder="Enter your password" required /></label>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <button class="button button-primary button-wide" type="submit" :disabled="loading">{{ loading ? 'Signing in…' : 'Sign in' }}<ArrowRight :size="17" /></button>
        </form>
        <p class="auth-switch">New to WealthPulse? <RouterLink to="/register">Create an account</RouterLink></p>
      </div>
      <div class="auth-legal"><span>WEALTHPULSE</span><span>YOUR MONEY STAYS YOURS</span></div>
    </section>
  </main>
</template>