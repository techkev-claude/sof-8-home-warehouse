<script setup>
import { computed } from 'vue'

const props = defineProps({
  status: { type: String, required: true },
})

const config = {
  stored: { label: 'Eingelagert', classes: 'bg-green-100 text-green-700' },
  in_use: { label: 'In Verwendung', classes: 'bg-amber-100 text-amber-700' },
  defect: { label: 'Defekt', classes: 'bg-red-100 text-red-700' },
  lost: { label: 'Vermisst', classes: 'bg-gray-200 text-gray-600' },
}

const current = computed(() => config[props.status] ?? { label: props.status, classes: 'bg-gray-200 text-gray-600' })
</script>

<template>
  <span
    class="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-bold"
    :class="current.classes"
  >
    {{ current.label }}
  </span>
</template>
