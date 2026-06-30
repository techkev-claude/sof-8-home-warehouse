<script setup>
import { ref, onMounted, reactive } from 'vue'
import { useLocationsStore } from '../stores/locations'
import { useAuthStore } from '../stores/auth'
import LocationTree from '../components/locations/LocationTree.vue'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'

const locationsStore = useLocationsStore()
const authStore = useAuthStore()

const loading = ref(true)
const error = ref('')

const showForm = ref(false)
const formMode = ref('add') // 'add' | 'edit'
const formSubmitting = ref(false)
const form = reactive({ id: null, name: '', description: '', parent_id: null })

const showDeleteConfirm = ref(false)
const pendingDelete = ref(null)
const deleteError = ref('')

onMounted(async () => {
  loading.value = true
  try {
    await locationsStore.fetchAll()
  } catch {
    error.value = 'Orte konnten nicht geladen werden.'
  } finally {
    loading.value = false
  }
})

function openAddForm(parentId) {
  formMode.value = 'add'
  Object.assign(form, { id: null, name: '', description: '', parent_id: parentId })
  showForm.value = true
}

function openEditForm(node) {
  formMode.value = 'edit'
  Object.assign(form, {
    id: node.id,
    name: node.name,
    description: node.description ?? '',
    parent_id: node.parent_id,
  })
  showForm.value = true
}

async function submitForm() {
  formSubmitting.value = true
  error.value = ''
  try {
    const payload = {
      name: form.name.trim(),
      description: form.description.trim() || null,
      parent_id: form.parent_id,
    }
    if (formMode.value === 'add') {
      await locationsStore.createLocation(payload)
    } else {
      await locationsStore.updateLocation(form.id, payload)
    }
    showForm.value = false
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    formSubmitting.value = false
  }
}

function requestDelete(node) {
  pendingDelete.value = node
  deleteError.value = ''
  showDeleteConfirm.value = true
}

async function confirmDelete() {
  if (!pendingDelete.value) return
  try {
    await locationsStore.deleteLocation(pendingDelete.value.id)
    showDeleteConfirm.value = false
    pendingDelete.value = null
  } catch (err) {
    deleteError.value =
      err.response?.status === 409
        ? 'Ort kann nicht gelöscht werden: Er wird noch von Kabeln verwendet oder hat Unterorte.'
        : 'Löschen fehlgeschlagen.'
  }
}
</script>

<template>
  <div class="space-y-4 p-4">
    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ error }}</p>

    <div v-if="loading" class="py-10 text-center text-sm text-gray-400">Lädt...</div>

    <LocationTree
      v-else
      :tree="locationsStore.tree"
      :can-edit="authStore.canEdit"
      @add="openAddForm"
      @edit="openEditForm"
      @delete="requestDelete"
    />

    <!-- Add/Edit form -->
    <Teleport to="body">
      <div
        v-if="showForm"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
        @click.self="showForm = false"
      >
        <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
          <h3 class="text-base font-semibold text-gray-900">
            {{ formMode === 'add' ? 'Ort hinzufügen' : 'Ort bearbeiten' }}
          </h3>
          <form class="mt-4 space-y-4" @submit.prevent="submitForm">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Name *</label>
              <input
                v-model="form.name"
                type="text"
                required
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
            <div class="flex gap-3">
              <button
                type="button"
                class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50"
                @click="showForm = false"
              >
                Abbrechen
              </button>
              <button
                type="submit"
                class="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50"
                :disabled="formSubmitting"
              >
                {{ formSubmitting ? 'Speichern...' : 'Speichern' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <ConfirmDialog
      :open="showDeleteConfirm"
      title="Ort löschen?"
      :message="deleteError || 'Dieser Ort wird unwiderruflich gelöscht.'"
      @confirm="confirmDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>
