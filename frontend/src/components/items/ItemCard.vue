<script setup>
import { computed } from 'vue'
import ItemStatusBadge from './ItemStatusBadge.vue'

const props = defineProps({
  item: { type: Object, required: true },
})

const primaryImage = computed(() => {
  if (!props.item.images?.length) return null
  return props.item.images.find((img) => img.is_primary) ?? props.item.images[0]
})

const connectorSummary = computed(() => {
  const parts = [props.item.connector_a, props.item.connector_b].filter(Boolean)
  return parts.length ? parts.join(' → ') : null
})
</script>

<template>
  <RouterLink
    :to="`/items/${item.id}`"
    class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-3 shadow-sm hover:border-indigo-200"
  >
    <div class="h-14 w-14 shrink-0 overflow-hidden rounded-lg bg-gray-100">
      <img
        v-if="primaryImage"
        :src="`/images/${primaryImage.thumbnail_filename}`"
        :alt="item.name"
        class="h-full w-full object-cover"
      />
      <div v-else class="flex h-full w-full items-center justify-center text-gray-300">
        <svg class="h-7 w-7" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="1.5"
            d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M4 8h16M4 4h16v16H4V4z"
          />
        </svg>
      </div>
    </div>
    <div class="min-w-0 flex-1">
      <p class="truncate text-sm font-semibold text-gray-900">{{ item.name }}</p>
      <p v-if="connectorSummary" class="truncate text-xs text-gray-500">{{ connectorSummary }}</p>
    </div>
    <ItemStatusBadge :status="item.status" />
  </RouterLink>
</template>
