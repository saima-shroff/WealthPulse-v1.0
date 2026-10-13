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
    const { data } = await api.post('/auth/register', { email: email.value, password: password.value })
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
      <div class="auth-quote"><span class="eyebrow">A FRESH START, FINANCIALLY</span><h1>Make room<br />for the plans<br /><em>that matter.</em></h1><div class="auth-orbit"><span></span><span></span><span></span><div class="orbit-center"><ArrowRight :size="25" /></div></div></div>
      <div class="auth-art-footer">Small habits. A clearer big picture.</div>
    </section>
    <section class="auth-form-side">
      <div class="auth-form-wrap">
        <div class="auth-form-icon"><LockKeyhole :size="19" /></div>
        <div class="eyebrow">GET STARTED</div>
        <h2>Create your account</h2>
        <p class="auth-subtitle">One secure place to see the whole picture.</p>
        <form class="form-stack" @submit.prevent="submit">
          <label>Email address<input v-model.trim="email" type="email" autocomplete="email" placeholder="you@example.com" required /></label>
          <label>Password<input v-model="password" type="password" autocomplete="new-password" placeholder="At least 10 characters" minlength="10" maxlength="128" required /></label>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <button class="button button-primary button-wide" type="submit" :disabled="loading">{{ loading ? 'Creating account…' : 'Create account' }}<ArrowRight :size="17" /></button>
        </form>
        <p class="auth-switch">Already have an account? <RouterLink to="/login">Sign in</RouterLink></p>
      </div>
      <div class="auth-legal"><span>WEALTHPULSE</span><span>YOUR MONEY STAYS YOURS</span></div>
    </section>
  </main>
</template>