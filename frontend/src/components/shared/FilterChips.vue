<script setup>
const props = defineProps({
  modelValue: { type: String, default: '' },
})
const emit = defineEmits(['update:modelValue'])

const options = [
  { value: '', label: 'Alle' },
  { value: 'stored', label: 'Eingelagert' },
  { value: 'in_use', label: 'In Verwendung' },
  { value: 'defect', label: 'Defekt' },
  { value: 'lost', label: 'Vermisst' },
]
</script>

<template>
  <div class="flex gap-2 overflow-x-auto pb-1" style="scrollbar-width: none">
    <button
      v-for="opt in options"
      :key="opt.value"
      type="button"
      class="shrink-0 rounded-full px-3 py-1.5 text-sm font-medium transition-colors"
      :class="
        modelValue === opt.value
          ? 'bg-indigo-600 text-white'
          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
      "
      @click="emit('update:modelValue', opt.value)"
    >
      {{ opt.label }}
    </button>
  </div>
</template>
