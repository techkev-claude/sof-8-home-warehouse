<script setup>
defineProps({
  open: { type: Boolean, default: false },
  title: { type: String, default: 'Wirklich löschen?' },
  message: { type: String, default: 'Diese Aktion kann nicht rückgängig gemacht werden.' },
  confirmLabel: { type: String, default: 'Löschen' },
  cancelLabel: { type: String, default: 'Abbrechen' },
  danger: { type: Boolean, default: true },
})
const emit = defineEmits(['confirm', 'cancel'])
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
      @click.self="emit('cancel')"
    >
      <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
        <h3 class="text-base font-semibold text-gray-900">{{ title }}</h3>
        <p class="mt-1 text-sm text-gray-500">{{ message }}</p>
        <div class="mt-5 flex gap-3">
          <button
            type="button"
            class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="emit('cancel')"
          >
            {{ cancelLabel }}
          </button>
          <button
            type="button"
            class="flex-1 rounded-lg py-2.5 text-sm font-medium text-white"
            :class="danger ? 'bg-red-600 hover:bg-red-700' : 'bg-indigo-600 hover:bg-indigo-700'"
            @click="emit('confirm')"
          >
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
