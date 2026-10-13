<script setup>
import { onMounted, ref } from 'vue'
import { ArrowDownLeft, ArrowUpRight, Landmark, Pencil, Plus, Trash2, WalletCards, X } from 'lucide-vue-next'
import { api, currency, errorMessage } from '../services/api'

const accounts = ref([])
const transactions = ref([])
const dialog = ref(null)
const editingId = ref(null)
const form = ref({ name: '', type: 'Checking', balance: '0' })
const error = ref('')
const loading = ref(true)
const saving = ref(false)
const accountTypes = ['Checking', 'Savings', 'Cash', 'Credit']
const accountIcons = { Checking: Landmark, Savings: WalletCards, Cash: ArrowDownLeft, Credit: ArrowUpRight }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [accountResponse, transactionResponse] = await Promise.all([api.get('/accounts'), api.get('/transactions', { params: { per_page: 100 } })])
    accounts.value = accountResponse.data
    transactions.value = transactionResponse.data.items
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingId.value = null
  form.value = { name: '', type: 'Checking', balance: '0' }
  error.value = ''
  dialog.value?.showModal()
}

function openEdit(account) {
  editingId.value = account.id
  form.value = { name: account.name, type: account.type, balance: account.balance }
  error.value = ''
  dialog.value?.showModal()
}

async function submit() {
  saving.value = true
  error.value = ''
  try {
    const payload = { name: form.value.name, type: form.value.type }
    if (!editingId.value) payload.balance = Number(form.value.balance)
    if (editingId.value) await api.put(`/accounts/${editingId.value}`, payload)
    else await api.post('/accounts', payload)
    dialog.value?.close()
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    saving.value = false
  }
}

async function remove(account) {
  if (!window.confirm(`Delete ${account.name}?`)) return
  try {
    await api.delete(`/accounts/${account.id}`)
    await load()
  } catch (failure) {
    error.value = errorMessage(failure)
  }
}

onMounted(load)
</script>

<template>
  <div class="page-heading"><div><span class="eyebrow">YOUR FINANCIAL HOME</span><h1>Accounts</h1><p>See your money across every account.</p></div><button class="button button-primary" @click="openCreate"><Plus :size="17" />Add account</button></div>
  <p v-if="error" class="notice notice-error" role="alert">{{ error }}</p>
  <div v-if="loading" class="loading-line">Loading accounts…</div>
  <template v-else>
    <section class="account-summary-strip"><div><span class="eyebrow">TOTAL BALANCE</span><strong>{{ currency(accounts.reduce((sum, account) => sum + Number(account.balance), 0)) }}</strong></div><span class="summary-divider"></span><div><span class="eyebrow">OPEN ACCOUNTS</span><strong>{{ accounts.length }}</strong></div><span class="summary-note">Balances update automatically with each transaction.</span></section>
    <section v-if="accounts.length" class="account-grid"><article v-for="account in accounts" :key="account.id" class="account-card"><div class="account-card-top"><span class="account-type-icon"><component :is="accountIcons[account.type] || WalletCards" :size="19" /></span><div class="account-actions"><button class="icon-button" title="Edit account" @click="openEdit(account)"><Pencil :size="15" /></button><button class="icon-button danger-icon" title="Delete account" @click="remove(account)"><Trash2 :size="15" /></button></div></div><span class="account-kind">{{ account.type }}</span><h2>{{ account.name }}</h2><strong class="account-balance">{{ currency(account.balance) }}</strong><div class="account-card-foot"><span><i class="status-dot"></i>Active</span><span>•••• {{ String(account.id).padStart(4, '0') }}</span></div></article></section>
    <section v-else class="panel empty-state"><div class="empty-ledger-mark"><WalletCards :size="21" /></div><h2>Start with an account</h2><p>Add a checking, savings, cash, or credit account to see your finances in one place.</p><button class="button button-primary" @click="openCreate"><Plus :size="16" />Add account</button></section>
    <section v-if="accounts.length" class="panel account-activity"><div class="panel-heading"><div><span class="eyebrow">A LITTLE CONTEXT</span><h2>Account activity</h2></div><RouterLink to="/transactions" class="inline-link">Open ledger <ArrowUpRight :size="14" /></RouterLink></div><div v-if="transactions.length" class="account-mini-list"><div v-for="item in transactions.slice(0, 4)" :key="item.id" class="account-mini-row"><span class="transaction-icon" :class="item.type === 'Income' ? 'income-icon' : 'expense-icon'">{{ item.type === 'Income' ? '+' : '−' }}</span><span class="account-mini-description"><strong>{{ item.category_name }}</strong><small>{{ item.account_name }} · {{ item.date }}</small></span><strong :class="item.type === 'Income' ? 'amount-income' : ''">{{ item.type === 'Income' ? '+' : '−' }}{{ currency(item.amount) }}</strong></div></div><p v-else class="muted-copy">Transactions will show here once you start recording activity.</p></section>
  </template>
  <dialog ref="dialog" class="form-dialog" @click.self="dialog?.close()"><form class="dialog-content" @submit.prevent="submit"><div class="dialog-heading"><div><span class="eyebrow">{{ editingId ? 'ACCOUNT DETAILS' : 'NEW ACCOUNT' }}</span><h2>{{ editingId ? 'Edit account' : 'Add account' }}</h2></div><button class="icon-button" type="button" title="Close" @click="dialog?.close()"><X :size="18" /></button></div><label>Account name<input v-model.trim="form.name" maxlength="80" placeholder="Everyday checking" required /></label><label>Account type<select v-model="form.type"><option v-for="type in accountTypes" :key="type">{{ type }}</option></select></label><label v-if="!editingId">Starting balance<input v-model="form.balance" type="number" step="0.01" placeholder="0.00" required /></label><p v-else class="muted-copy">Account balance is maintained by its transactions.</p><p v-if="error" class="form-error" role="alert">{{ error }}</p><div class="dialog-actions"><button class="button button-quiet" type="button" @click="dialog?.close()">Cancel</button><button class="button button-primary" type="submit" :disabled="saving">{{ saving ? 'Saving…' : editingId ? 'Save changes' : 'Add account' }}</button></div></form></dialog>
</template>