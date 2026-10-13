<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowDownUp, ChevronLeft, ChevronRight, Pencil, Plus, Search, Trash2, X } from 'lucide-vue-next'
import { api, currency, errorMessage } from '../services/api'

const transactions = ref([])
const accounts = ref([])
const categories = ref([])
const page = ref(1)
const pages = ref(1)
const total = ref(0)
const perPage = 10
const filters = ref({ start_date: '', end_date: '', account_id: '', category_id: '' })
const dialog = ref(null)
const categoryDialog = ref(null)
const form = ref({ type: 'Expense', account_id: '', category_id: '', amount: '', date: new Date().toISOString().slice(0, 10), notes: '' })
const categoryForm = ref({ name: '', type: 'Expense' })
const editingId = ref(null)
const error = ref('')
const loading = ref(true)
const saving = ref(false)
const savingCategory = ref(false)
const expenseCategories = computed(() => categories.value.filter((item) => item.type === form.value.type))
const visibleRange = computed(() => total.value ? `${(page.value - 1) * perPage + 1}–${Math.min(page.value * perPage, total.value)} of ${total.value}` : '0 transactions')

async function load() {
  loading.value = true
  error.value = ''
  try {
    const params = Object.fromEntries(Object.entries({ ...filters.value, page: page.value, per_page: perPage }).filter(([, value]) => value !== ''))
    const [transactionResponse, accountResponse, categoryResponse] = await Promise.all([
      api.get('/transactions', { params }), api.get('/accounts'), api.get('/categories'),
    ])
    transactions.value = transactionResponse.data.items
    pages.value = transactionResponse.data.pages
    total.value = transactionResponse.data.total
    accounts.value = accountResponse.data
    categories.value = categoryResponse.data
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { type: 'Expense', account_id: accounts.value[0]?.id || '', category_id: '', amount: '', date: new Date().toISOString().slice(0, 10), notes: '' }
  if (!categories.value.some((item) => item.type === 'Expense')) error.value = 'Create an expense category before adding a transaction.'
  else { error.value = ''; form.value.category_id = expenseCategories.value[0]?.id || ''; dialog.value?.showModal() }
}

function openEdit(item) {
  editingId.value = item.id
  form.value = { type: item.type, account_id: item.account_id, category_id: item.category_id, amount: item.amount, date: item.date, notes: item.notes }
  dialog.value?.showModal()
}

function closeDialog() {
  dialog.value?.close()
}

function openCategoryDialog() {
  categoryForm.value = { name: '', type: 'Expense' }
  error.value = ''
  categoryDialog.value?.showModal()
}

async function submitCategory() {
  savingCategory.value = true
  error.value = ''
  try {
    await api.post('/categories', categoryForm.value)
    categoryDialog.value?.close()
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    savingCategory.value = false
  }
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { ...form.value, account_id: Number(form.value.account_id), category_id: Number(form.value.category_id), amount: Number(form.value.amount) }
    if (editingId.value) await api.put(`/transactions/${editingId.value}`, payload)
    else await api.post('/transactions', payload)
    closeDialog()
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    saving.value = false
  }
}

async function remove(item) {
  if (!window.confirm(`Delete the ${item.category_name} transaction for ${currency(item.amount)}?`)) return
  try {
    await api.delete(`/transactions/${item.id}`)
    if (transactions.value.length === 1 && page.value > 1) page.value -= 1
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  }
}

function changeType() {
  form.value.category_id = expenseCategories.value[0]?.id || ''
}

function applyFilters() {
  page.value = 1
  load()
}

onMounted(load)
</script>

<template>
  <div class="page-heading"><div><span class="eyebrow">YOUR FINANCIAL STORY</span><h1>Transactions</h1><p>Every detail, accounted for.</p></div><div class="heading-actions"><button class="button button-outline category-button" :disabled="loading" @click="openCategoryDialog"><Plus :size="15" />Category</button><button class="button button-primary" :disabled="loading" @click="openCreate"><Plus :size="17" />Add transaction</button></div></div>
  <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>
  <section class="filter-bar" aria-label="Filter transactions"><div class="filter-title"><Search :size="16" />Filter by</div><label>From<input v-model="filters.start_date" type="date" @change="applyFilters" /></label><label>To<input v-model="filters.end_date" type="date" @change="applyFilters" /></label><label>Account<select v-model="filters.account_id" @change="applyFilters"><option value="">All accounts</option><option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option></select></label><label>Category<select v-model="filters.category_id" @change="applyFilters"><option value="">All categories</option><option v-for="category in categories" :key="category.id" :value="category.id">{{ category.name }}</option></select></label><button class="text-button clear-filter" @click="filters = { start_date: '', end_date: '', account_id: '', category_id: '' }; applyFilters()"><X :size="14" />Clear</button></section>
  <section class="panel ledger-panel"><div class="ledger-toolbar"><div><span class="eyebrow">ACTIVITY LEDGER</span><h2>All transactions <span class="count-pill">{{ total }}</span></h2></div><div class="ledger-range"><ArrowDownUp :size="15" />{{ visibleRange }}</div></div><div v-if="loading" class="loading-line">Loading transactions…</div><div v-else-if="transactions.length" class="table-scroll"><table class="data-table transaction-table"><thead><tr><th>TRANSACTION</th><th>ACCOUNT</th><th>DATE</th><th class="align-right">AMOUNT</th><th class="actions-column"></th></tr></thead><tbody><tr v-for="item in transactions" :key="item.id"><td><span class="transaction-cell"><span class="transaction-icon" :class="item.type === 'Income' ? 'income-icon' : 'expense-icon'">{{ item.type === 'Income' ? '+' : '−' }}</span><span><strong>{{ item.category_name }}</strong><small>{{ item.notes || item.type }}</small></span></span></td><td>{{ item.account_name }}</td><td>{{ new Date(`${item.date}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }) }}</td><td class="align-right amount-cell" :class="item.type === 'Income' ? 'amount-income' : ''">{{ item.type === 'Income' ? '+' : '−' }}{{ currency(item.amount) }}</td><td class="row-actions"><button class="icon-button" title="Edit transaction" @click="openEdit(item)"><Pencil :size="15" /></button><button class="icon-button danger-icon" title="Delete transaction" @click="remove(item)"><Trash2 :size="15" /></button></td></tr></tbody></table></div><div v-else class="empty-ledger"><div class="empty-ledger-mark"><Search :size="21" /></div><h3>No transactions found</h3><p>Try adjusting the filters, or add a transaction to get started.</p><button class="button button-outline" @click="openCreate"><Plus :size="16" />Add transaction</button></div><div class="pagination"><span>{{ visibleRange }}</span><div><button class="icon-button" title="Previous page" :disabled="page <= 1" @click="page -= 1; load()"><ChevronLeft :size="17" /></button><span class="page-indicator">{{ page }} / {{ pages }}</span><button class="icon-button" title="Next page" :disabled="page >= pages" @click="page += 1; load()"><ChevronRight :size="17" /></button></div></div></section>
  <dialog ref="dialog" class="form-dialog" @click.self="closeDialog"><form class="dialog-content" @submit.prevent="submit"><div class="dialog-heading"><div><span class="eyebrow">{{ editingId ? 'UPDATE ENTRY' : 'NEW ENTRY' }}</span><h2>{{ editingId ? 'Edit transaction' : 'Add transaction' }}</h2></div><button class="icon-button" type="button" title="Close" @click="closeDialog"><X :size="18" /></button></div><div class="type-switch" role="group" aria-label="Transaction type"><button type="button" :class="{ selected: form.type === 'Expense' }" @click="form.type = 'Expense'; changeType()">Expense</button><button type="button" :class="{ selected: form.type === 'Income' }" @click="form.type = 'Income'; changeType()">Income</button></div><label>Amount<input v-model="form.amount" type="number" min="0.01" step="0.01" placeholder="0.00" required /></label><div class="form-two-col"><label>Account<select v-model="form.account_id" required><option value="" disabled>Select account</option><option v-for="account in accounts" :key="account.id" :value="account.id">{{ account.name }}</option></select></label><label>Category<select v-model="form.category_id" required><option value="" disabled>Select category</option><option v-for="category in expenseCategories" :key="category.id" :value="category.id">{{ category.name }}</option></select></label></div><label>Date<input v-model="form.date" type="date" required /></label><label>Note <span class="optional-label">OPTIONAL</span><input v-model.trim="form.notes" maxlength="500" placeholder="A small detail worth remembering" /></label><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="dialog-actions"><button class="button button-quiet" type="button" @click="closeDialog">Cancel</button><button class="button button-primary" type="submit" :disabled="saving">{{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add transaction' }}</button></div></form></dialog>
  <dialog ref="categoryDialog" class="form-dialog" @click.self="categoryDialog?.close()"><form class="dialog-content" @submit.prevent="submitCategory"><div class="dialog-heading"><div><span class="eyebrow">PERSONALISE YOUR LEDGER</span><h2>New category</h2></div><button class="icon-button" type="button" title="Close" @click="categoryDialog?.close()"><X :size="18" /></button></div><label>Category name<input v-model.trim="categoryForm.name" maxlength="80" placeholder="e.g. Groceries" required /></label><label>Category type<select v-model="categoryForm.type"><option>Expense</option><option>Income</option></select></label><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="dialog-actions"><button class="button button-quiet" type="button" @click="categoryDialog?.close()">Cancel</button><button class="button button-primary" type="submit" :disabled="savingCategory">{{ savingCategory ? 'Saving…' : 'Create category' }}</button></div></form></dialog>
</template>