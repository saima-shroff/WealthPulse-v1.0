<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowRight, ChartNoAxesCombined, CircleCheck, Plus, X } from 'lucide-vue-next'
import { api, currency, errorMessage } from '../services/api'

const budgets = ref([])
const categories = ref([])
const month = ref(new Date().toISOString().slice(0, 7))
const dialog = ref(null)
const form = ref({ category_id: '', monthly_limit: '' })
const error = ref('')
const loading = ref(true)
const saving = ref(false)
const spentTotal = computed(() => budgets.value.reduce((sum, item) => sum + Number(item.spent), 0))
const limitTotal = computed(() => budgets.value.reduce((sum, item) => sum + Number(item.monthly_limit), 0))
const remainingTotal = computed(() => limitTotal.value - spentTotal.value)
const expenseCategories = computed(() => categories.value.filter((item) => item.type === 'Expense' && !budgets.value.some((budget) => budget.category_id === item.id)))

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [budgetResponse, categoryResponse] = await Promise.all([api.get('/budgets', { params: { month: month.value } }), api.get('/categories')])
    budgets.value = budgetResponse.data
    categories.value = categoryResponse.data
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  error.value = ''
  form.value = { category_id: expenseCategories.value[0]?.id || '', monthly_limit: '' }
  if (!expenseCategories.value.length) error.value = 'Add an expense category before creating a budget.'
  else dialog.value?.showModal()
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    await api.post('/budgets', { category_id: Number(form.value.category_id), monthly_limit: Number(form.value.monthly_limit), month_year: month.value })
    dialog.value?.close()
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    saving.value = false
  }
}

function progress(item) {
  return Math.min(100, Number(item.spent) / Number(item.monthly_limit) * 100)
}

onMounted(load)
</script>

<template>
  <div class="page-heading"><div><span class="eyebrow">A PLAN FOR EVERY CATEGORY</span><h1>Budgets</h1><p>Give your priorities a little room to breathe.</p></div><button class="button button-primary" :disabled="!expenseCategories.length && !loading" @click="openCreate"><Plus :size="17" />Set a budget</button></div>
  <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>
  <section class="budget-month-control"><label for="budget-month">MONTH</label><input id="budget-month" v-model="month" type="month" @change="load" /><span>Tracking {{ new Date(`${month}-01T12:00:00`).toLocaleDateString('en-US', { month: 'long', year: 'numeric' }) }}</span></section>
  <div v-if="loading" class="loading-line">Loading your plan…</div>
  <template v-else>
    <section class="budget-overview"><div class="budget-overview-head"><div><span class="eyebrow">MONTHLY SPENDING PLAN</span><h2>{{ currency(spentTotal) }} <span>of {{ currency(limitTotal) }}</span></h2></div><div class="budget-ring" :style="{ '--progress': `${limitTotal ? Math.min(100, spentTotal / limitTotal * 100) : 0}%` }"><strong>{{ limitTotal ? Math.round(spentTotal / limitTotal * 100) : 0 }}<small>%</small></strong></div></div><div class="budget-overview-track"><span :style="{ width: `${limitTotal ? Math.min(100, spentTotal / limitTotal * 100) : 0}%` }"></span></div><div class="budget-overview-foot"><span>{{ currency(spentTotal) }} spent</span><span :class="remainingTotal < 0 ? 'over-budget' : ''">{{ currency(Math.abs(remainingTotal)) }} {{ remainingTotal < 0 ? 'over plan' : 'left to spend' }}</span></div></section>
    <div class="section-title-row"><div><span class="eyebrow">CATEGORY BREAKDOWN</span><h2>Your monthly limits</h2></div><span class="budget-count">{{ budgets.length }} {{ budgets.length === 1 ? 'category' : 'categories' }}</span></div>
    <section v-if="budgets.length" class="budget-list"><article v-for="(budget, index) in budgets" :key="budget.id" class="budget-row"><div class="budget-row-icon" :class="`budget-tone-${index % 4}`"><ChartNoAxesCombined :size="18" /></div><div class="budget-row-main"><div class="budget-row-top"><div><h3>{{ budget.category_name }}</h3><span>{{ currency(budget.spent) }} spent of {{ currency(budget.monthly_limit) }}</span></div><strong :class="progress(budget) >= 100 ? 'over-budget' : ''">{{ Math.round(progress(budget)) }}%</strong></div><div class="progress-track"><span :class="progress(budget) >= 100 ? 'progress-over' : ''" :style="{ width: `${progress(budget)}%` }"></span></div><div class="budget-row-bottom"><span v-if="progress(budget) >= 100" class="over-budget"><CircleCheck :size="14" />Limit reached</span><span v-else>{{ currency(Number(budget.monthly_limit) - Number(budget.spent)) }} remaining</span><span>{{ new Date(`${month}-01T12:00:00`).toLocaleDateString('en-US', { month: 'short' }) }}</span></div></div></article></section>
    <section v-else class="panel empty-state"><div class="empty-ledger-mark"><ChartNoAxesCombined :size="21" /></div><h2>Your plan starts here</h2><p>Choose an expense category and set a monthly limit. You can track every category at a glance.</p><div class="empty-state-actions"><button class="button button-primary" :disabled="!expenseCategories.length" @click="openCreate"><Plus :size="16" />Set a budget</button><RouterLink to="/transactions" class="inline-link">Go to transactions <ArrowRight :size="14" /></RouterLink></div><span v-if="!expenseCategories.length" class="empty-hint">First, add an expense category in Transactions.</span></section>
  </template>
  <dialog ref="dialog" class="form-dialog" @click.self="dialog?.close()"><form class="dialog-content" @submit.prevent="submit"><div class="dialog-heading"><div><span class="eyebrow">MONTHLY PLAN · {{ month }}</span><h2>Set a budget</h2></div><button class="icon-button" type="button" title="Close" @click="dialog?.close()"><X :size="18" /></button></div><label>Expense category<select v-model="form.category_id" required><option value="" disabled>Select category</option><option v-for="category in expenseCategories" :key="category.id" :value="category.id">{{ category.name }}</option></select></label><label>Monthly limit<input v-model="form.monthly_limit" type="number" min="0.01" step="0.01" placeholder="0.00" required /></label><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="dialog-actions"><button class="button button-quiet" type="button" @click="dialog?.close()">Cancel</button><button class="button button-primary" type="submit" :disabled="saving">{{ saving ? 'Saving…' : 'Save budget' }}</button></div></form></dialog>
</template>