<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { useCategoriesStore } from '../stores/categories'
import { useUsagePurposesStore } from '../stores/usagePurposes'
import * as usersApi from '../api/users'
import ConfirmDialog from '../components/shared/ConfirmDialog.vue'

const authStore = useAuthStore()
const categoriesStore = useCategoriesStore()
const usagePurposesStore = useUsagePurposesStore()
const router = useRouter()

const tabs = computed(() => {
  const base = [
    { key: 'categories', label: 'Kategorien' },
    { key: 'purposes', label: 'Verwendungszwecke' },
  ]
  if (authStore.isAdmin) base.push({ key: 'users', label: 'Benutzer' })
  return base
})
const activeTab = ref('categories')

onMounted(() => {
  categoriesStore.fetchCategories()
  usagePurposesStore.fetchPurposes()
  if (authStore.isAdmin) loadUsers()
})

/* ---------- Categories ---------- */
const showCategoryForm = ref(false)
const categoryFormMode = ref('add')
const categoryForm = ref({ id: null, name: '', icon: '', color: '', description: '' })
const categorySubmitting = ref(false)
const categoryError = ref('')
const showCategoryDeleteConfirm = ref(false)
const pendingCategoryDelete = ref(null)
const categoryDeleteError = ref('')

function openAddCategory() {
  categoryFormMode.value = 'add'
  categoryForm.value = { id: null, name: '', icon: '', color: '', description: '' }
  showCategoryForm.value = true
}
function openEditCategory(cat) {
  categoryFormMode.value = 'edit'
  categoryForm.value = { id: cat.id, name: cat.name, icon: cat.icon ?? '', color: cat.color ?? '', description: cat.description ?? '' }
  showCategoryForm.value = true
}
async function submitCategory() {
  categorySubmitting.value = true
  categoryError.value = ''
  try {
    const payload = {
      name: categoryForm.value.name.trim(),
      icon: categoryForm.value.icon.trim() || null,
      color: categoryForm.value.color.trim() || null,
      description: categoryForm.value.description.trim() || null,
    }
    if (categoryFormMode.value === 'add') {
      await categoriesStore.createCategory(payload)
    } else {
      await categoriesStore.updateCategory(categoryForm.value.id, payload)
    }
    showCategoryForm.value = false
  } catch (err) {
    categoryError.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    categorySubmitting.value = false
  }
}
function requestDeleteCategory(cat) {
  pendingCategoryDelete.value = cat
  categoryDeleteError.value = ''
  showCategoryDeleteConfirm.value = true
}
async function confirmDeleteCategory() {
  try {
    await categoriesStore.deleteCategory(pendingCategoryDelete.value.id)
    showCategoryDeleteConfirm.value = false
  } catch (err) {
    categoryDeleteError.value =
      err.response?.status === 409
        ? 'Kategorie wird noch von Kabeln verwendet und kann nicht gelöscht werden.'
        : 'Löschen fehlgeschlagen.'
  }
}

/* ---------- Usage purposes ---------- */
const showPurposeForm = ref(false)
const purposeFormMode = ref('add')
const purposeForm = ref({ id: null, name: '', description: '', requires_note: false })
const purposeSubmitting = ref(false)
const purposeError = ref('')
const showPurposeDeleteConfirm = ref(false)
const pendingPurposeDelete = ref(null)
const purposeDeleteError = ref('')

function openAddPurpose() {
  purposeFormMode.value = 'add'
  purposeForm.value = { id: null, name: '', description: '', requires_note: false }
  showPurposeForm.value = true
}
function openEditPurpose(purpose) {
  purposeFormMode.value = 'edit'
  purposeForm.value = {
    id: purpose.id,
    name: purpose.name,
    description: purpose.description ?? '',
    requires_note: purpose.requires_note,
  }
  showPurposeForm.value = true
}
async function submitPurpose() {
  purposeSubmitting.value = true
  purposeError.value = ''
  try {
    const payload = {
      name: purposeForm.value.name.trim(),
      description: purposeForm.value.description.trim() || null,
      requires_note: purposeForm.value.requires_note,
    }
    if (purposeFormMode.value === 'add') {
      await usagePurposesStore.createPurpose(payload)
    } else {
      await usagePurposesStore.updatePurpose(purposeForm.value.id, payload)
    }
    showPurposeForm.value = false
  } catch (err) {
    purposeError.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    purposeSubmitting.value = false
  }
}
function requestDeletePurpose(purpose) {
  pendingPurposeDelete.value = purpose
  purposeDeleteError.value = ''
  showPurposeDeleteConfirm.value = true
}
async function confirmDeletePurpose() {
  try {
    await usagePurposesStore.deletePurpose(pendingPurposeDelete.value.id)
    showPurposeDeleteConfirm.value = false
  } catch (err) {
    purposeDeleteError.value =
      err.response?.status === 409
        ? 'Verwendungszweck wird noch von Kabeln verwendet und kann nicht gelöscht werden.'
        : 'Löschen fehlgeschlagen.'
  }
}

/* ---------- Users (admin only) ---------- */
const users = ref([])
const usersLoading = ref(false)
const showUserForm = ref(false)
const userFormMode = ref('add')
const userForm = ref({ id: null, username: '', password: '', role: 'member', is_active: true })
const userSubmitting = ref(false)
const userError = ref('')
const showUserDeleteConfirm = ref(false)
const pendingUserDelete = ref(null)
const userDeleteError = ref('')

async function loadUsers() {
  usersLoading.value = true
  try {
    users.value = await usersApi.listUsers()
  } finally {
    usersLoading.value = false
  }
}
function openAddUser() {
  userFormMode.value = 'add'
  userForm.value = { id: null, username: '', password: '', role: 'member', is_active: true }
  showUserForm.value = true
}
function openEditUser(user) {
  userFormMode.value = 'edit'
  userForm.value = { id: user.id, username: user.username, password: '', role: user.role, is_active: user.is_active }
  showUserForm.value = true
}
async function submitUser() {
  userSubmitting.value = true
  userError.value = ''
  try {
    if (userFormMode.value === 'add') {
      await usersApi.createUser({
        username: userForm.value.username.trim(),
        password: userForm.value.password,
        role: userForm.value.role,
      })
    } else {
      const payload = { role: userForm.value.role, is_active: userForm.value.is_active }
      if (userForm.value.password) payload.password = userForm.value.password
      await usersApi.updateUser(userForm.value.id, payload)
    }
    showUserForm.value = false
    await loadUsers()
  } catch (err) {
    userError.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    userSubmitting.value = false
  }
}
function requestDeleteUser(user) {
  pendingUserDelete.value = user
  userDeleteError.value = ''
  showUserDeleteConfirm.value = true
}
async function confirmDeleteUser() {
  try {
    await usersApi.deleteUser(pendingUserDelete.value.id)
    showUserDeleteConfirm.value = false
    await loadUsers()
  } catch {
    userDeleteError.value = 'Löschen fehlgeschlagen.'
  }
}

function handleLogout() {
  authStore.logout()
  router.replace('/login')
}
</script>

<template>
  <div class="space-y-4 p-4">
    <div class="flex gap-2 overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.key"
        type="button"
        class="shrink-0 rounded-full px-3 py-1.5 text-sm font-medium"
        :class="activeTab === tab.key ? 'bg-indigo-600 text-white' : 'bg-gray-100 text-gray-600'"
        @click="activeTab = tab.key"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Kategorien -->
    <div v-if="activeTab === 'categories'" class="space-y-2">
      <div
        v-for="cat in categoriesStore.categories"
        :key="cat.id"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-3"
      >
        <span class="text-xl">{{ cat.icon || '📁' }}</span>
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-gray-900">{{ cat.name }}</p>
          <p v-if="cat.description" class="truncate text-xs text-gray-500">{{ cat.description }}</p>
        </div>
        <template v-if="authStore.canEdit">
          <button type="button" class="text-xs font-medium text-indigo-600" @click="openEditCategory(cat)">
            Bearbeiten
          </button>
          <button type="button" class="text-xs font-medium text-red-600" @click="requestDeleteCategory(cat)">
            Löschen
          </button>
        </template>
      </div>
      <p v-if="!categoriesStore.categories.length" class="py-6 text-center text-sm text-gray-400">
        Keine Kategorien vorhanden.
      </p>
      <button
        v-if="authStore.canEdit"
        type="button"
        class="w-full rounded-lg border border-dashed border-indigo-300 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        @click="openAddCategory"
      >
        + Kategorie hinzufügen
      </button>
    </div>

    <!-- Verwendungszwecke -->
    <div v-if="activeTab === 'purposes'" class="space-y-2">
      <div
        v-for="purpose in usagePurposesStore.purposes"
        :key="purpose.id"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-3"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-gray-900">{{ purpose.name }}</p>
          <p v-if="purpose.description" class="truncate text-xs text-gray-500">{{ purpose.description }}</p>
          <span
            v-if="purpose.requires_note"
            class="mt-1 inline-block rounded-full bg-indigo-50 px-2 py-0.5 text-[11px] font-medium text-indigo-600"
          >
            Zusatzinformation erforderlich
          </span>
        </div>
        <template v-if="authStore.canEdit">
          <button type="button" class="text-xs font-medium text-indigo-600" @click="openEditPurpose(purpose)">
            Bearbeiten
          </button>
          <button type="button" class="text-xs font-medium text-red-600" @click="requestDeletePurpose(purpose)">
            Löschen
          </button>
        </template>
      </div>
      <p v-if="!usagePurposesStore.purposes.length" class="py-6 text-center text-sm text-gray-400">
        Keine Verwendungszwecke vorhanden.
      </p>
      <button
        v-if="authStore.canEdit"
        type="button"
        class="w-full rounded-lg border border-dashed border-indigo-300 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        @click="openAddPurpose"
      >
        + Verwendungszweck hinzufügen
      </button>
    </div>

    <!-- Benutzer -->
    <div v-if="activeTab === 'users' && authStore.isAdmin" class="space-y-2">
      <div v-if="usersLoading" class="py-10 text-center text-sm text-gray-400">Lädt...</div>
      <div
        v-for="user in users"
        :key="user.id"
        class="flex items-center gap-3 rounded-xl border border-gray-200 bg-white p-3"
      >
        <div class="min-w-0 flex-1">
          <p class="truncate text-sm font-medium text-gray-900">
            {{ user.username }}
            <span v-if="!user.is_active" class="ml-1 text-xs font-normal text-gray-400">(deaktiviert)</span>
          </p>
          <p class="text-xs text-gray-500">{{ user.role }}</p>
        </div>
        <button type="button" class="text-xs font-medium text-indigo-600" @click="openEditUser(user)">
          Bearbeiten
        </button>
        <button
          v-if="user.id !== authStore.user?.id"
          type="button"
          class="text-xs font-medium text-red-600"
          @click="requestDeleteUser(user)"
        >
          Löschen
        </button>
      </div>
      <button
        type="button"
        class="w-full rounded-lg border border-dashed border-indigo-300 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
        @click="openAddUser"
      >
        + Benutzer hinzufügen
      </button>
    </div>

    <div class="pt-4">
      <button
        type="button"
        class="w-full rounded-lg border border-red-300 py-2.5 text-sm font-medium text-red-600 hover:bg-red-50"
        @click="handleLogout"
      >
        Abmelden
      </button>
    </div>

    <!-- Category form dialog -->
    <Teleport to="body">
      <div
        v-if="showCategoryForm"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
        @click.self="showCategoryForm = false"
      >
        <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
          <h3 class="text-base font-semibold text-gray-900">
            {{ categoryFormMode === 'add' ? 'Kategorie hinzufügen' : 'Kategorie bearbeiten' }}
          </h3>
          <p v-if="categoryError" class="mt-2 text-sm text-red-600">{{ categoryError }}</p>
          <form class="mt-4 space-y-4" @submit.prevent="submitCategory">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Name *</label>
              <input v-model="categoryForm.name" type="text" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="mb-1 block text-sm font-medium text-gray-700">Icon (Emoji)</label>
                <input v-model="categoryForm.icon" type="text" placeholder="🔌" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
              <div>
                <label class="mb-1 block text-sm font-medium text-gray-700">Farbe</label>
                <input v-model="categoryForm.color" type="text" placeholder="#4f46e5" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
              </div>
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Beschreibung</label>
              <textarea v-model="categoryForm.description" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div class="flex gap-3">
              <button type="button" class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50" @click="showCategoryForm = false">
                Abbrechen
              </button>
              <button type="submit" class="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50" :disabled="categorySubmitting">
                {{ categorySubmitting ? 'Speichern...' : 'Speichern' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- Usage purpose form dialog -->
    <Teleport to="body">
      <div
        v-if="showPurposeForm"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
        @click.self="showPurposeForm = false"
      >
        <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
          <h3 class="text-base font-semibold text-gray-900">
            {{ purposeFormMode === 'add' ? 'Verwendungszweck hinzufügen' : 'Verwendungszweck bearbeiten' }}
          </h3>
          <p v-if="purposeError" class="mt-2 text-sm text-red-600">{{ purposeError }}</p>
          <form class="mt-4 space-y-4" @submit.prevent="submitPurpose">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Name *</label>
              <input v-model="purposeForm.name" type="text" required class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Beschreibung</label>
              <textarea v-model="purposeForm.description" rows="2" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500" />
            </div>
            <label class="flex items-center gap-2 text-sm text-gray-700">
              <input v-model="purposeForm.requires_note" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              Zusatzinformation erfassen
            </label>
            <div class="flex gap-3">
              <button type="button" class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50" @click="showPurposeForm = false">
                Abbrechen
              </button>
              <button type="submit" class="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50" :disabled="purposeSubmitting">
                {{ purposeSubmitting ? 'Speichern...' : 'Speichern' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <!-- User form dialog -->
    <Teleport to="body">
      <div
        v-if="showUserForm"
        class="fixed inset-0 z-50 flex items-end justify-center bg-black/40 sm:items-center"
        @click.self="showUserForm = false"
      >
        <div class="w-full max-w-[480px] rounded-t-xl bg-white p-5 shadow-lg sm:rounded-xl">
          <h3 class="text-base font-semibold text-gray-900">
            {{ userFormMode === 'add' ? 'Benutzer hinzufügen' : 'Benutzer bearbeiten' }}
          </h3>
          <p v-if="userError" class="mt-2 text-sm text-red-600">{{ userError }}</p>
          <form class="mt-4 space-y-4" @submit.prevent="submitUser">
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Benutzername *</label>
              <input
                v-model="userForm.username"
                type="text"
                required
                :disabled="userFormMode === 'edit'"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:bg-gray-100 disabled:text-gray-400"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">
                Passwort {{ userFormMode === 'edit' ? '(leer lassen, um es nicht zu ändern)' : '*' }}
              </label>
              <input
                v-model="userForm.password"
                type="password"
                :required="userFormMode === 'add'"
                class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label class="mb-1 block text-sm font-medium text-gray-700">Rolle</label>
              <select v-model="userForm.role" class="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500">
                <option value="admin">Administrator</option>
                <option value="member">Mitglied</option>
                <option value="viewer">Betrachter</option>
              </select>
            </div>
            <label v-if="userFormMode === 'edit'" class="flex items-center gap-2 text-sm text-gray-700">
              <input v-model="userForm.is_active" type="checkbox" class="h-4 w-4 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500" />
              Aktiv
            </label>
            <div class="flex gap-3">
              <button type="button" class="flex-1 rounded-lg border border-gray-300 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50" @click="showUserForm = false">
                Abbrechen
              </button>
              <button type="submit" class="flex-1 rounded-lg bg-indigo-600 py-2.5 text-sm font-semibold text-white hover:bg-indigo-700 disabled:opacity-50" :disabled="userSubmitting">
                {{ userSubmitting ? 'Speichern...' : 'Speichern' }}
              </button>
            </div>
          </form>
        </div>
      </div>
    </Teleport>

    <ConfirmDialog
      :open="showCategoryDeleteConfirm"
      title="Kategorie löschen?"
      :message="categoryDeleteError || 'Diese Kategorie wird unwiderruflich gelöscht.'"
      @confirm="confirmDeleteCategory"
      @cancel="showCategoryDeleteConfirm = false"
    />
    <ConfirmDialog
      :open="showPurposeDeleteConfirm"
      title="Verwendungszweck löschen?"
      :message="purposeDeleteError || 'Dieser Verwendungszweck wird unwiderruflich gelöscht.'"
      @confirm="confirmDeletePurpose"
      @cancel="showPurposeDeleteConfirm = false"
    />
    <ConfirmDialog
      :open="showUserDeleteConfirm"
      title="Benutzer löschen?"
      :message="userDeleteError || 'Dieser Benutzer wird unwiderruflich gelöscht.'"
      @confirm="confirmDeleteUser"
      @cancel="showUserDeleteConfirm = false"
    />
  </div>
</template>
