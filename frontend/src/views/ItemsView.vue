<script setup>
import { onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useItemsStore } from '../stores/items'
import ItemCard from '../components/items/ItemCard.vue'
import SearchBar from '../components/shared/SearchBar.vue'
import FilterChips from '../components/shared/FilterChips.vue'
import { useAuthStore } from '../stores/auth'

const itemsStore = useItemsStore()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

if (typeof route.query.status === 'string') {
  itemsStore.setFilters({ status: route.query.status })
}

onMounted(() => {
  itemsStore.fetchItems()
})

watch(
  () => itemsStore.filters.status,
  (status) => {
    router.replace({ query: { ...route.query, status: status || undefined } })
    itemsStore.fetchItems()
  },
)

watch(
  () => itemsStore.filters.search,
  () => {
    itemsStore.fetchItems()
  },
)

function updateSearch(value) {
  itemsStore.setFilters({ search: value })
}
</script>

<template>
  <div class="space-y-4 p-4">
    <SearchBar
      :model-value="itemsStore.filters.search"
      placeholder="Kabel suchen..."
      @update:model-value="updateSearch"
    />
    <FilterChips
      :model-value="itemsStore.filters.status"
      @update:model-value="(v) => itemsStore.setFilters({ status: v })"
    />

    <div v-if="itemsStore.loading && !itemsStore.items.length" class="py-10 text-center text-sm text-gray-400">
      Lädt...
    </div>

    <div v-else-if="!itemsStore.items.length" class="py-10 text-center text-sm text-gray-400">
      Keine Kabel gefunden.
    </div>

    <div v-else class="space-y-2">
      <ItemCard v-for="item in itemsStore.items" :key="item.id" :item="item" />
    </div>

    <button
      v-if="itemsStore.hasMore && itemsStore.items.length"
      type="button"
      class="w-full rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 disabled:opacity-50"
      :disabled="itemsStore.loading"
      @click="itemsStore.loadMore"
    >
      {{ itemsStore.loading ? 'Lädt...' : 'Mehr laden' }}
    </button>

  </div>

  <RouterLink
    v-if="authStore.canEdit"
    to="/items/add"
    class="fixed bottom-20 z-10 flex h-14 w-14 items-center justify-center rounded-full bg-indigo-600 text-2xl text-white shadow-lg hover:bg-indigo-700"
    style="right: max(1.25rem, calc(50vw - 240px + 1.25rem))"
  >
    +
  </RouterLink>
</template>
