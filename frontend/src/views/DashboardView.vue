<script setup>
import { computed, onMounted, ref } from 'vue'
import { ArrowDownRight, ArrowRight, ArrowUpRight, Plus, Sparkles, Wallet } from 'lucide-vue-next'
import { Doughnut, Line } from 'vue-chartjs'
import { ArcElement, Chart as ChartJS, Filler, Legend, LineElement, PointElement, CategoryScale, LinearScale, Tooltip } from 'chart.js'
import { api, currency, errorMessage } from '../services/api'

ChartJS.register(ArcElement, CategoryScale, Filler, Legend, LinearScale, LineElement, PointElement, Tooltip)

const accounts = ref([])
const transactions = ref([])
const budgets = ref([])
const error = ref('')
const loading = ref(true)
const thisMonth = new Date().toISOString().slice(0, 7)
const thisMonthTransactions = computed(() => transactions.value.filter((item) => item.date.startsWith(thisMonth)))
const income = computed(() => thisMonthTransactions.value.filter((item) => item.type === 'Income').reduce((sum, item) => sum + Number(item.amount), 0))
const expenses = computed(() => thisMonthTransactions.value.filter((item) => item.type === 'Expense').reduce((sum, item) => sum + Number(item.amount), 0))
const netWorth = computed(() => accounts.value.reduce((sum, account) => sum + Number(account.balance), 0))
const recentTransactions = computed(() => transactions.value.slice(0, 5))
const categoryTotals = computed(() => {
  const totals = new Map()
  thisMonthTransactions.value.filter((item) => item.type === 'Expense').forEach((item) => totals.set(item.category_name, (totals.get(item.category_name) || 0) + Number(item.amount)))
  return [...totals.entries()].sort((a, b) => b[1] - a[1]).slice(0, 5)
})
const categoryColors = ['#c4523d', '#80a28d', '#dcb759', '#456c61', '#db8a62']
const categoryChart = computed(() => ({
  labels: categoryTotals.value.map(([name]) => name),
  datasets: [{ data: categoryTotals.value.map(([, amount]) => amount), backgroundColor: categoryColors, borderWidth: 0, hoverOffset: 5 }],
}))
const cashFlowChart = computed(() => {
  const months = Array.from({ length: 6 }, (_, index) => {
    const date = new Date()
    date.setDate(1)
    date.setMonth(date.getMonth() - (5 - index))
    return date
  })
  const labels = months.map((date) => date.toLocaleDateString('en-US', { month: 'short' }))
  const incomeData = months.map((date) => transactions.value.filter((item) => item.date.startsWith(date.toISOString().slice(0, 7)) && item.type === 'Income').reduce((sum, item) => sum + Number(item.amount), 0))
  const expenseData = months.map((date) => transactions.value.filter((item) => item.date.startsWith(date.toISOString().slice(0, 7)) && item.type === 'Expense').reduce((sum, item) => sum + Number(item.amount), 0))
  return { labels, datasets: [
    { label: 'Income', data: incomeData, borderColor: '#426f5b', backgroundColor: 'rgba(66,111,91,.10)', fill: true, tension: .38, pointRadius: 3, pointBackgroundColor: '#426f5b' },
    { label: 'Expenses', data: expenseData, borderColor: '#c4523d', backgroundColor: 'rgba(196,82,61,.05)', fill: true, tension: .38, pointRadius: 3, pointBackgroundColor: '#c4523d' },
  ] }
})
const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, tooltip: { displayColors: true, padding: 10 } }, scales: { x: { grid: { display: false }, border: { display: false }, ticks: { color: '#87908a' } }, y: { grid: { color: 'rgba(40,60,48,.08)' }, border: { display: false }, ticks: { color: '#87908a', callback: (value) => `$${value}` } } } }
const doughnutOptions = { responsive: true, maintainAspectRatio: false, cutout: '73%', plugins: { legend: { display: false }, tooltip: { padding: 10 } } }

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [accountResponse, transactionResponse, budgetResponse] = await Promise.all([
      api.get('/accounts'), api.get('/transactions', { params: { per_page: 100 } }), api.get('/budgets'),
    ])
    accounts.value = accountResponse.data
    transactions.value = transactionResponse.data.items
    budgets.value = budgetResponse.data
  } catch (failure) {
    error.value = errorMessage(failure)
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <div class="page-heading">
    <div><span class="eyebrow">YOUR FINANCIAL SNAPSHOT</span><h1>Good money starts with a clear view.</h1><p>Everything you need to know, in one place.</p></div>
    <RouterLink class="button button-primary" to="/transactions"><Plus :size="17" />Add transaction</RouterLink>
  </div>
  <p v-if="error" class="notice notice-error">{{ error }} <button class="text-button" @click="load">Retry</button></p>
  <div v-if="loading" class="loading-line">Gathering your financial picture…</div>
  <template v-else>
    <section class="metric-grid" aria-label="Monthly financial summary">
      <article class="metric-card metric-net"><div class="metric-top"><span>NET WORTH</span><span class="metric-icon"><Wallet :size="17" /></span></div><strong>{{ currency(netWorth) }}</strong><div class="metric-foot"><span class="metric-foot-dot"></span>{{ accounts.length }} active {{ accounts.length === 1 ? 'account' : 'accounts' }}</div></article>
      <article class="metric-card"><div class="metric-top"><span>INCOME THIS MONTH</span><span class="metric-icon metric-green"><ArrowDownRight :size="17" /></span></div><strong>{{ currency(income) }}</strong><div class="metric-foot">Across {{ thisMonthTransactions.filter((item) => item.type === 'Income').length }} deposits</div></article>
      <article class="metric-card"><div class="metric-top"><span>SPENT THIS MONTH</span><span class="metric-icon metric-red"><ArrowUpRight :size="17" /></span></div><strong>{{ currency(expenses) }}</strong><div class="metric-foot">{{ thisMonthTransactions.filter((item) => item.type === 'Expense').length }} transactions recorded</div></article>
      <article class="metric-card metric-plan"><div class="metric-top"><span>PLANNED SPENDING</span><span class="metric-icon metric-yellow"><Sparkles :size="17" /></span></div><strong>{{ budgets.length }}</strong><div class="metric-foot"><RouterLink to="/budgets">{{ budgets.length ? 'Budgets keeping you on track' : 'Set your first monthly budget' }} <ArrowRight :size="13" /></RouterLink></div></article>
    </section>

    <section class="dashboard-grid">
      <article class="panel cash-panel"><div class="panel-heading"><div><span class="eyebrow">THE LAST SIX MONTHS</span><h2>Cash flow</h2></div><div class="chart-legend"><span><i class="legend-dot legend-income"></i>Income</span><span><i class="legend-dot legend-expense"></i>Expenses</span></div></div><div class="line-chart-wrap"><Line :data="cashFlowChart" :options="chartOptions" /></div></article>
      <article class="panel spending-panel"><div class="panel-heading"><div><span class="eyebrow">THIS MONTH</span><h2>Where it went</h2></div><RouterLink to="/transactions" class="panel-arrow" title="View transactions"><ArrowRight :size="17" /></RouterLink></div><div v-if="categoryTotals.length" class="spending-content"><div class="doughnut-wrap"><Doughnut :data="categoryChart" :options="doughnutOptions" /><div class="doughnut-center"><strong>{{ currency(expenses) }}</strong><span>TOTAL SPENT</span></div></div><div class="category-legend"><div v-for="([name, amount], index) in categoryTotals" :key="name" class="category-legend-row"><span class="category-name"><i class="legend-dot" :style="{ backgroundColor: categoryColors[index] }"></i>{{ name }}</span><strong>{{ currency(amount) }}</strong></div></div></div><div v-else class="empty-chart">Your spending categories will appear here.</div></article>
    </section>

    <section class="panel recent-panel"><div class="panel-heading"><div><span class="eyebrow">THE LATEST</span><h2>Recent activity</h2></div><RouterLink to="/transactions" class="inline-link">All transactions <ArrowRight :size="14" /></RouterLink></div><div v-if="recentTransactions.length" class="table-scroll"><table class="data-table"><thead><tr><th>TRANSACTION</th><th>ACCOUNT</th><th>DATE</th><th class="align-right">AMOUNT</th></tr></thead><tbody><tr v-for="item in recentTransactions" :key="item.id"><td><span class="transaction-cell"><span class="transaction-icon" :class="item.type === 'Income' ? 'income-icon' : 'expense-icon'">{{ item.type === 'Income' ? '+' : '−' }}</span><span><strong>{{ item.category_name }}</strong><small>{{ item.notes || item.type }}</small></span></span></td><td>{{ item.account_name }}</td><td>{{ new Date(`${item.date}T12:00:00`).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }) }}</td><td class="align-right amount-cell" :class="item.type === 'Income' ? 'amount-income' : ''">{{ item.type === 'Income' ? '+' : '−' }}{{ currency(item.amount) }}</td></tr></tbody></table></div><div v-else class="empty-row"><span>Your ledger is ready.</span><RouterLink to="/transactions">Add your first transaction <ArrowRight :size="14" /></RouterLink></div></section>
  </template>
</template>