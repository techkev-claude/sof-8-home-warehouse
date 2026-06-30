<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCategoriesStore } from '../stores/categories'
import { useLocationsStore } from '../stores/locations'
import { useUsagePurposesStore } from '../stores/usagePurposes'
import { getItem, updateItem, deleteItem, checkoutItem, checkinItem } from '../api/items'
import { uploadImages, deleteImage, setPrimaryImage } from '../api/images'
import ItemStatusBadge from '../components/items/ItemStatusBadge.vue'
import ItemForm from '../components/items/ItemForm.vue'
import ImageUpload from '../components/shared/ImageUpload.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'
import CheckoutDialog from '../components/items/CheckoutDialog.vue'
import CheckinDialog from '../components/items/CheckinDialog.vue'

const props = defineProps({ id: { type: [String, Number], required: true } })

const router = useRouter()
const authStore = useAuthStore()
const categoriesStore = useCategoriesStore()
const locationsStore = useLocationsStore()
const usagePurposesStore = useUsagePurposesStore()

const item = ref(null)
const loading = ref(true)
const error = ref('')
const editing = ref(false)
const savingForm = ref(false)
const uploadingImages = ref(false)

const showDeleteConfirm = ref(false)
const showCheckoutDialog = ref(false)
const showCheckinDialog = ref(false)
const actionSubmitting = ref(false)
const activeImageIndex = ref(0)

async function loadItem() {
  loading.value = true
  error.value = ''
  try {
    item.value = await getItem(props.id)
    activeImageIndex.value = 0
  } catch (err) {
    error.value = err.response?.status === 404 ? 'Kabel wurde nicht gefunden.' : 'Laden fehlgeschlagen.'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadItem()
  if (!categoriesStore.loaded) categoriesStore.fetchCategories()
  if (!locationsStore.loaded) locationsStore.fetchAll()
  if (!usagePurposesStore.loaded) usagePurposesStore.fetchPurposes()
})

const categoryName = computed(() => {
  if (!item.value?.category_id) return null
  return categoriesStore.byId(item.value.category_id)?.name ?? null
})

const locationName = computed(() => {
  if (!item.value?.location_id) return null
  return locationsStore.byId(item.value.location_id)?.name ?? null
})

const usagePurposeName = computed(() => {
  if (!item.value?.usage_purpose_id) return null
  return usagePurposesStore.byId(item.value.usage_purpose_id)?.name ?? null
})

const sortedImages = computed(() => {
  if (!item.value?.images) return []
  return [...item.value.images].sort((a, b) => a.sort_order - b.sort_order)
})

const activeImage = computed(() => sortedImages.value[activeImageIndex.value] ?? null)

async function handleFormSubmit(payload) {
  savingForm.value = true
  error.value = ''
  try {
    item.value = await updateItem(props.id, payload)
    editing.value = false
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    savingForm.value = false
  }
}

async function handleAddFiles(files) {
  uploadingImages.value = true
  try {
    await uploadImages(props.id, files)
    await loadItem()
  } catch {
    error.value = 'Bilder konnten nicht hochgeladen werden.'
  } finally {
    uploadingImages.value = false
  }
}

async function handleRemoveImage(img) {
  try {
    await deleteImage(props.id, img.id)
    await loadItem()
  } catch {
    error.value = 'Bild konnte nicht gelöscht werden.'
  }
}

async function handleSetPrimary(img) {
  try {
    await setPrimaryImage(props.id, img.id)
    await loadItem()
  } catch {
    error.value = 'Titelbild konnte nicht gesetzt werden.'
  }
}

async function handleDelete() {
  actionSubmitting.value = true
  try {
    await deleteItem(props.id)
    router.push('/items')
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Löschen fehlgeschlagen.'
    showDeleteConfirm.value = false
  } finally {
    actionSubmitting.value = false
  }
}

async function handleCheckout(payload) {
  actionSubmitting.value = true
  error.value = ''
  try {
    item.value = await checkoutItem(props.id, payload)
    showCheckoutDialog.value = false
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Auschecken fehlgeschlagen.'
  } finally {
    actionSubmitting.value = false
  }
}

async function handleCheckin(payload) {
  actionSubmitting.value = true
  error.value = ''
  try {
    item.value = await checkinItem(props.id, payload)
    showCheckinDialog.value = false
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Einlagern fehlgeschlagen.'
  } finally {
    actionSubmitting.value = false
  }
}

function formatDate(value) {
  if (!value) return '—'
  return new Date(value).toLocaleString('de-DE', { dateStyle: 'medium', timeStyle: 'short' })
}
</script>

<template>
  <div class="p-4">
    <div v-if="loading" class="py-10 text-center text-sm text-gray-400">Lädt...</div>
    <div v-else-if="!item" class="py-10 text-center text-sm text-gray-400">
      {{ error || 'Kabel wurde nicht gefunden.' }}
    </div>

    <div v-else class="space-y-5">
      <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ error }}</p>

      <!-- Image gallery -->
      <div>
        <div class="aspect-square w-full overflow-hidden rounded-xl bg-gray-100">
          <img
            v-if="activeImage"
            :src="`/images/${activeImage.filename}`"
            :alt="item.name"
            class="h-full w-full object-cover"
          />
          <div v-else class="flex h-full w-full items-center justify-center text-gray-300">
            <svg class="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="1.5"
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14M4 8h16M4 4h16v16H4V4z"
              />
            </svg>
          </div>
        </div>
        <div v-if="sortedImages.length > 1" class="mt-2 flex gap-2 overflow-x-auto">
          <button
            v-for="(img, index) in sortedImages"
            :key="img.id"
            type="button"
            class="h-14 w-14 shrink-0 overflow-hidden rounded-lg border-2"
            :class="index === activeImageIndex ? 'border-indigo-600' : 'border-transparent'"
            @click="activeImageIndex = index"
          >
            <img :src="`/images/${img.thumbnail_filename}`" alt="" class="h-full w-full object-cover" />
          </button>
        </div>
      </div>

      <!-- Header -->
      <div class="flex items-start justify-between gap-3">
        <div>
          <h2 class="text-lg font-bold text-gray-900">{{ item.name }}</h2>
          <p v-if="item.description" class="mt-1 text-sm text-gray-500">{{ item.description }}</p>
        </div>
        <ItemStatusBadge :status="item.status" />
      </div>

      <!-- Details -->
      <div class="rounded-xl border border-gray-200 bg-white p-4 text-sm">
        <dl class="space-y-2">
          <div v-if="categoryName" class="flex justify-between">
            <dt class="text-gray-500">Kategorie</dt>
            <dd class="font-medium text-gray-900">{{ categoryName }}</dd>
          </div>
          <div v-if="item.connector_a || item.connector_b" class="flex justify-between">
            <dt class="text-gray-500">Stecker</dt>
            <dd class="font-medium text-gray-900">
              {{ [item.connector_a, item.connector_b].filter(Boolean).join(' → ') }}
            </dd>
          </div>
          <div v-if="item.cable_length_cm" class="flex justify-between">
            <dt class="text-gray-500">Länge</dt>
            <dd class="font-medium text-gray-900">{{ item.cable_length_cm }} cm</dd>
          </div>
          <div v-if="item.color" class="flex justify-between">
            <dt class="text-gray-500">Farbe</dt>
            <dd class="font-medium text-gray-900">{{ item.color }}</dd>
          </div>
          <div v-if="item.brand" class="flex justify-between">
            <dt class="text-gray-500">Marke</dt>
            <dd class="font-medium text-gray-900">{{ item.brand }}</dd>
          </div>
          <div v-if="item.status === 'stored'" class="flex justify-between">
            <dt class="text-gray-500">Lagerort</dt>
            <dd class="font-medium text-gray-900">{{ locationName ?? '—' }}</dd>
          </div>
          <div v-if="item.status === 'in_use'" class="flex justify-between">
            <dt class="text-gray-500">Verwendungszweck</dt>
            <dd class="font-medium text-gray-900">{{ usagePurposeName ?? '—' }}</dd>
          </div>
          <div v-if="item.status === 'in_use' && item.usage_note" class="flex justify-between gap-3">
            <dt class="shrink-0 text-gray-500">Zusatzinfo</dt>
            <dd class="text-right font-medium text-gray-900">{{ item.usage_note }}</dd>
          </div>
          <div class="flex justify-between">
            <dt class="text-gray-500">Eingelagert am</dt>
            <dd class="font-medium text-gray-900">{{ formatDate(item.stored_at) }}</dd>
          </div>
          <div v-if="item.checked_out_at" class="flex justify-between">
            <dt class="text-gray-500">Ausgecheckt am</dt>
            <dd class="font-medium text-gray-900">{{ formatDate(item.checked_out_at) }}</dd>
          </div>
        </dl>
      </div>

      <!-- Actions -->
      <div v-if="authStore.canEdit" class="space-y-2">
        <button
          v-if="item.status === 'stored'"
          type="button"
          class="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
          @click="showCheckoutDialog = true"
        >
          Auschecken
        </button>
        <button
          v-if="item.status === 'in_use'"
          type="button"
          class="w-full rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700"
          @click="showCheckinDialog = true"
        >
          Einlagern
        </button>
        <button
          type="button"
          class="w-full rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
          @click="editing = !editing"
        >
          {{ editing ? 'Bearbeiten schließen' : 'Bearbeiten' }}
        </button>
        <button
          type="button"
          class="w-full rounded-lg border border-red-300 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50"
          @click="showDeleteConfirm = true"
        >
          Kabel löschen
        </button>
      </div>

      <!-- Edit form -->
      <div v-if="editing" class="space-y-4 rounded-xl border border-gray-200 bg-white p-4">
        <div>
          <h3 class="mb-2 text-sm font-semibold text-gray-700">Fotos</h3>
          <ImageUpload
            :existing-images="sortedImages"
            :uploading="uploadingImages"
            @add-files="handleAddFiles"
            @remove-existing="handleRemoveImage"
            @set-primary="handleSetPrimary"
          />
        </div>
        <ItemForm
          :model-value="item"
          :categories="categoriesStore.categories"
          :locations="locationsStore.flat"
          submit-label="Änderungen speichern"
          :submitting="savingForm"
          @submit="handleFormSubmit"
        />
      </div>
    </div>

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Kabel löschen?"
      message="Dieses Kabel und alle zugehörigen Bilder werden unwiderruflich gelöscht."
      @confirm="handleDelete"
      @cancel="showDeleteConfirm = false"
    />

    <CheckoutDialog
      :open="showCheckoutDialog"
      :purposes="usagePurposesStore.purposes"
      :submitting="actionSubmitting"
      @confirm="handleCheckout"
      @cancel="showCheckoutDialog = false"
    />

    <CheckinDialog
      :open="showCheckinDialog"
      :locations="locationsStore.flat"
      :submitting="actionSubmitting"
      @confirm="handleCheckin"
      @cancel="showCheckinDialog = false"
    />
  </div>
</template>
