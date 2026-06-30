<script setup>
import { ref, computed, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  purposes: { type: Array, default: () => [] },
  submitting: { type: Boolean, default: false },
})
const emit = defineEmits(['confirm', 'cancel'])

const usagePurposeId = ref('')
const usageNote = ref('')
const touched = ref(false)

const selectedPurpose = computed(() =>
  props.purposes.find((p) => p.id === Number(usagePurposeId.value)),
)
const noteRequired = computed(() => selectedPurpose.value?.requires_note === true)
const noteMissing = computed(() => noteRequired.value && !usageNote.value.trim())

watch(
  () => props.open,
  (isOpen) => {
    if (isOpen) {
      usagePurposeId.value = ''
      usageNote.value = ''
      touched.value = false
    }
  },
)

function handleConfirm() {
  touched.value = true
  if (noteMissing.value) return
  emit('confirm', {
    usage_purpose_id: usagePurposeId.value ? Number(usagePurposeId.value) : null,
    usage_note: usageNote.value.trim() || null,
  })
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
        <h3 class="text-base font-semibold text-gray-900">Kabel auschecken</h3>
        <p class="mt-1 text-sm text-gray-500">Wofür wird das Kabel verwendet?</p>

        <div class="mt-4">
          <label class="mb-1 block text-sm font-medium text-gray-700">Verwendungszweck</label>
          <select
            v-model="usagePurposeId"
            class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
          >
            <option value="">Kein Verwendungszweck</option>
            <option v-for="purpose in purposes" :key="purpose.id" :value="purpose.id">
              {{ purpose.name }}
            </option>
          </select>
        </div>

        <div v-if="selectedPurpose" class="mt-4">
          <label class="mb-1 block text-sm font-medium text-gray-700">
            Zusatzinformation
            <span v-if="noteRequired" class="text-red-600">* erforderlich</span>
            <span v-else class="text-gray-400">(optional)</span>
          </label>
          <textarea
            v-model="usageNote"
            rows="2"
            placeholder="z.B. wofür genau wird das Kabel benötigt?"
            class="w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1"
            :class="
              touched && noteMissing
                ? 'border-red-400 focus:border-red-500 focus:ring-red-500'
                : 'border-gray-300 focus:border-indigo-500 focus:ring-indigo-500'
            "
          />
          <p v-if="touched && noteMissing" class="mt-1 text-xs text-red-600">
            Für diesen Verwendungszweck ist eine Zusatzinformation erforderlich.
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
            {{ submitting ? 'Bitte warten...' : 'Auschecken' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>
