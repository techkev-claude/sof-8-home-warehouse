<script setup>
import { reactive, watch } from 'vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  categories: { type: Array, default: () => [] },
  locations: { type: Array, default: () => [] },
  submitLabel: { type: String, default: 'Speichern' },
  submitting: { type: Boolean, default: false },
})
const emit = defineEmits(['submit'])

const form = reactive({
  name: props.modelValue.name ?? '',
  description: props.modelValue.description ?? '',
  category_id: props.modelValue.category_id ?? '',
  connector_a: props.modelValue.connector_a ?? '',
  connector_b: props.modelValue.connector_b ?? '',
  cable_length_cm: props.modelValue.cable_length_cm ?? '',
  color: props.modelValue.color ?? '',
  brand: props.modelValue.brand ?? '',
  location_id: props.modelValue.location_id ?? '',
})

watch(
  () => props.modelValue,
  (val) => {
    Object.assign(form, {
      name: val.name ?? '',
      description: val.description ?? '',
      category_id: val.category_id ?? '',
      connector_a: val.connector_a ?? '',
      connector_b: val.connector_b ?? '',
      cable_length_cm: val.cable_length_cm ?? '',
      color: val.color ?? '',
      brand: val.brand ?? '',
      location_id: val.location_id ?? '',
    })
  },
)

function locationLabel(loc) {
  return loc.name
}

function handleSubmit() {
  const payload = {
    name: form.name.trim(),
    description: form.description.trim() || null,
    category_id: form.category_id || null,
    connector_a: form.connector_a.trim() || null,
    connector_b: form.connector_b.trim() || null,
    cable_length_cm: form.cable_length_cm === '' ? null : Number(form.cable_length_cm),
    color: form.color.trim() || null,
    brand: form.brand.trim() || null,
    location_id: form.location_id || null,
  }
  emit('submit', payload)
}
</script>

<template>
  <form class="space-y-4" @submit.prevent="handleSubmit">
    <div>
      <label class="mb-1 block text-sm font-medium text-gray-700">Name *</label>
      <input
        v-model="form.name"
        type="text"
        required
        placeholder="z.B. USB-C Ladekabel 2m"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium text-gray-700">Beschreibung</label>
      <textarea
        v-model="form.description"
        rows="2"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium text-gray-700">Kategorie</label>
      <select
        v-model="form.category_id"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      >
        <option value="">Keine Kategorie</option>
        <option v-for="cat in categories" :key="cat.id" :value="cat.id">
          {{ cat.icon ? cat.icon + ' ' : '' }}{{ cat.name }}
        </option>
      </select>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Stecker A</label>
        <input
          v-model="form.connector_a"
          type="text"
          placeholder="z.B. USB-C"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Stecker B</label>
        <input
          v-model="form.connector_b"
          type="text"
          placeholder="z.B. USB-A"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>
    </div>

    <div class="grid grid-cols-2 gap-3">
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Länge (cm)</label>
        <input
          v-model="form.cable_length_cm"
          type="number"
          min="0"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>
      <div>
        <label class="mb-1 block text-sm font-medium text-gray-700">Farbe</label>
        <input
          v-model="form.color"
          type="text"
          class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
        />
      </div>
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium text-gray-700">Marke</label>
      <input
        v-model="form.brand"
        type="text"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      />
    </div>

    <div>
      <label class="mb-1 block text-sm font-medium text-gray-700">Lagerort</label>
      <select
        v-model="form.location_id"
        class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
      >
        <option value="">Kein Lagerort</option>
        <option v-for="loc in locations" :key="loc.id" :value="loc.id">
          {{ locationLabel(loc) }}
        </option>
      </select>
    </div>

    <button
      type="submit"
      class="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
      :disabled="submitting"
    >
      {{ submitting ? 'Speichern...' : submitLabel }}
    </button>
  </form>
</template>
