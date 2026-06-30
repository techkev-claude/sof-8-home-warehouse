<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  locations: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])

const locationId = ref('')
const touched = ref(false)

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      locationId.value = ''
      touched.value = false
    }
  },
)

function handleConfirm() {
  touched.value = true
  if (!locationId.value) return
  emit('confirm', { location_id: Number(locationId.value) })
}
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
      @click.self="emit('cancel')"
    >
      <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
        <h3 class="text-base font-semibold text-gray-900">Kabel einlagern</h3>
        <p class="mt-1 text-sm text-gray-500">Wo wird das Kabel eingelagert?</p>

        <div class="mt-4">
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Lagerort <span class="text-red-600">*</span>
          </label>
          <select
            v-model="locationId"
            class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1"
            :class="
              touched && !locationId
                ? 'border-red-400 focus:border-red-500 focus:ring-red-500'
                : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            "
          >
            <option value="">Bitte wählen</option>
            <option v-for="loc in locations" :key="loc.id" :value="loc.id">
              {{ loc.name }}
            </option>
          </select>
          <p v-if="touched && !locationId" class="mt-1 text-xs text-red-600">
            Bitte einen Lagerort auswählen.
          </p>
        </div>

        <div class="mt-5 flex gap-3">
          <button
            type="button"
            class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
            @click="emit('cancel')"
          >
            Abbrechen
          </button>
          <button
            type="button"
            class="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
            :disabled="submitting"
            @click="handleConfirm"
          >
            {{ submitting ? 'Bitte warten...' : 'Einlagern' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
