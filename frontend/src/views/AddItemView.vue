<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ImageUpload from '../components/shared/ImageUpload.vue'
import ItemForm from '../components/items/ItemForm.vue'
import { useCategoriesStore } from '../stores/categories'
import { useLocationsStore } from '../stores/locations'
import { createItem } from '../api/items'
import { uploadImages } from '../api/images'

const router = useRouter()
const categoriesStore = useCategoriesStore()
const locationsStore = useLocationsStore()

const pendingFiles = ref([])
const submitting = ref(false)
const error = ref('')

onMounted(() => {
  if (!categoriesStore.loaded) categoriesStore.fetchCategories()
  if (!locationsStore.loaded) locationsStore.fetchAll()
})

function handleAddFiles(files) {
  pendingFiles.value.push(...files)
}

async function handleSubmit(payload) {
  error.value = ''
  submitting.value = true
  try {
    const item = await createItem(payload)
    if (pendingFiles.value.length) {
      try {
        await uploadImages(item.id, pendingFiles.value)
      } catch {
        // Item was created successfully even if the image upload failed;
        // surface this softly rather than blocking navigation.
        error.value = 'Kabel wurde gespeichert, aber Bilder konnten nicht hochgeladen werden.'
      }
    }
    router.push(`/items/${item.id}`)
  } catch (err) {
    error.value = err.response?.data?.detail ?? 'Speichern fehlgeschlagen.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="space-y-5 p-4">
    <div>
      <h2 class="mb-2 text-sm font-semibold text-gray-700">Fotos</h2>
      <ImageUpload @add-files="handleAddFiles" />
    </div>

    <p v-if="error" class="rounded-lg bg-red-50 px-3 py-2 text-sm text-red-600">{{ error }}</p>

    <ItemForm
      :model-value="{}"
      :categories="categoriesStore.categories"
      :locations="locationsStore.flat"
      submit-label="Kabel anlegen"
      :submitting="submitting"
      @submit="handleSubmit"
    />
  </div>
</template>
