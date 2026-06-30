<script setup>
import { ref, computed, onBeforeUnmount } from 'vue'

const props = defineProps({
  // Existing, already-uploaded images (objects with id, thumbnail_filename, is_primary).
  existingImages: { type: Array, default: () => [] },
  uploading: { type: Boolean, default: false },
})

const emit = defineEmits(['add-files', 'remove-existing', 'set-primary'])

const galleryInput = ref(null)
const cameraInput = ref(null)
const pendingFiles = ref([])
const pendingPreviews = ref([])

function openGallery() {
  galleryInput.value?.click()
}

function openCamera() {
  cameraInput.value?.click()
}

function handleFiles(event) {
  const files = Array.from(event.target.files || [])
  if (!files.length) return
  for (const file of files) {
    pendingFiles.value.push(file)
    pendingPreviews.value.push(URL.createObjectURL(file))
  }
  emit('add-files', files)
  event.target.value = ''
}

function removePending(index) {
  URL.revokeObjectURL(pendingPreviews.value[index])
  pendingFiles.value.splice(index, 1)
  pendingPreviews.value.splice(index, 1)
}

// Called by the parent once pending files have actually been uploaded, so the
// local preview list (which only exists until the real images come back from
// the API) can be cleared.
function clearPending() {
  pendingPreviews.value.forEach((url) => URL.revokeObjectURL(url))
  pendingFiles.value = []
  pendingPreviews.value = []
}

defineExpose({ clearPending })

onBeforeUnmount(() => {
  pendingPreviews.value.forEach((url) => URL.revokeObjectURL(url))
})

const hasImages = computed(() => props.existingImages.length > 0 || pendingPreviews.value.length > 0)
</script>

<template>
  <div>
    <div v-if="hasImages" class="mb-3 flex flex-wrap gap-2">
      <div
        v-for="img in existingImages"
        :key="img.id"
        class="group relative h-20 w-20 overflow-hidden rounded-lg border border-gray-200"
      >
        <img
          :src="`/images/${img.thumbnail_filename}`"
          :alt="'Bild ' + img.id"
          class="h-full w-full object-cover"
        />
        <span
          v-if="img.is_primary"
          class="absolute left-1 top-1 rounded-full bg-indigo-600 px-1.5 py-0.5 text-[10px] font-bold text-white"
        >
          Titelbild
        </span>
        <button
          v-if="!img.is_primary"
          type="button"
          class="absolute bottom-1 left-1 rounded bg-white/90 px-1.5 py-0.5 text-[10px] font-medium text-gray-700"
          @click="emit('set-primary', img)"
        >
          Als Titelbild
        </button>
        <button
          type="button"
          class="absolute right-1 top-1 flex h-5 w-5 items-center justify-center rounded-full bg-black/60 text-xs text-white"
          @click="emit('remove-existing', img)"
        >
          ✕
        </button>
      </div>

      <div
        v-for="(preview, index) in pendingPreviews"
        :key="'pending-' + index"
        class="relative h-20 w-20 overflow-hidden rounded-lg border border-gray-200 opacity-80"
      >
        <img :src="preview" alt="Vorschau" class="h-full w-full object-cover" />
        <button
          type="button"
          class="absolute right-1 top-1 flex h-5 w-5 items-center justify-center rounded-full bg-black/60 text-xs text-white"
          @click="removePending(index)"
        >
          ✕
        </button>
      </div>
    </div>

    <div class="flex gap-2">
      <button
        type="button"
        class="flex-1 rounded-lg border border-dashed border-gray-300 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50"
        :disabled="uploading"
        @click="openGallery"
      >
        Galerie
      </button>
      <button
        type="button"
        class="flex-1 rounded-lg border border-dashed border-gray-300 py-3 text-sm font-medium text-gray-600 hover:bg-gray-50"
        :disabled="uploading"
        @click="openCamera"
      >
        Foto aufnehmen
      </button>
    </div>

    <input
      ref="galleryInput"
      type="file"
      accept="image/*"
      multiple
      class="hidden"
      @change="handleFiles"
    />
    <input
      ref="cameraInput"
      type="file"
      accept="image/*"
      capture="environment"
      class="hidden"
      @change="handleFiles"
    />
  </div>
</template>
