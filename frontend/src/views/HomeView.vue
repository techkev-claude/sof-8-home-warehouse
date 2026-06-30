<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../stores/auth'
import { listItems } from '../api/items'

const authStore = useAuthStore()
const loading = ref(true)
const counts = ref({ stored: 0, in_use: 0, defect: 0, lost: 0 })
const total = ref(0)

async function loadCounts() {
  loading.value = true
  try {
    // The list endpoint has no count/aggregate response, so the dashboard
    // approximates totals per status using the max page size (200). Good
    // enough for a home inventory; won't be exact past 200 items per status.
    const [stored, inUse, defect, lost] = await Promise.all([
      listItems({ status: 'stored', limit: 200 }),
      listItems({ status: 'in_use', limit: 200 }),
      listItems({ status: 'defect', limit: 200 }),
      listItems({ status: 'lost', limit: 200 }),
    ])
    counts.value = {
      stored: stored.length,
      in_use: inUse.length,
      defect: defect.length,
      lost: lost.length,
    }
    total.value = counts.value.stored + counts.value.in_use + counts.value.defect + counts.value.lost
  } finally {
    loading.value = false
  }
}

onMounted(loadCounts)

const cards = [
  { key: 'stored', label: 'Eingelagert', classes: 'bg-green-50 text-green-700', filter: 'stored' },
  { key: 'in_use', label: 'In Verwendung', classes: 'bg-amber-50 text-amber-700', filter: 'in_use' },
  { key: 'defect', label: 'Defekt', classes: 'bg-red-50 text-red-700', filter: 'defect' },
  { key: 'lost', label: 'Vermisst', classes: 'bg-gray-100 text-gray-600', filter: 'lost' },
]
</script>

<template>
  <div class="space-y-6 p-4">
    <div>
      <p class="text-sm text-gray-500">Willkommen zurück{{ authStore.user ? ', ' + authStore.user.username : '' }}!</p>
      <p class="text-2xl font-bold text-gray-900">{{ total }} Kabel insgesamt</p>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <RouterLink
        v-for="card in cards"
        :key="card.key"
        :to="{ path: '/items', query: { status: card.filter } }"
        class="rounded-xl p-4 shadow-sm"
        :class="card.classes"
      >
        <p class="text-2xl font-bold">{{ loading ? '…' : counts[card.key] }}</p>
        <p class="text-sm font-medium">{{ card.label }}</p>
      </RouterLink>
    </div>

    <div class="space-y-2">
      <RouterLink
        to="/items/add"
        class="block w-full rounded-lg bg-indigo-600 py-3 text-center text-sm font-semibold text-white hover:bg-indigo-700"
      >
        + Neues Kabel hinzufügen
      </RouterLink>
      <RouterLink
        to="/items"
        class="block w-full rounded-lg border border-gray-300 py-3 text-center text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        Alle Kabel ansehen
      </RouterLink>
      <RouterLink
        to="/locations"
        class="block w-full rounded-lg border border-gray-300 py-3 text-center text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        Lagerorte verwalten
      </RouterLink>
    </div>
  </div>
</template>
