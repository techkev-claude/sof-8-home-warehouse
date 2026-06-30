<script setup>
import { ref, computed } from 'vue'

const props = defineProps({
  tree: { type: Array, required: true },
  canEdit: { type: Boolean, default: false },
})
const emit = defineEmits(['add', 'edit', 'delete'])

// Path of location ids representing the current drill-down position.
const path = ref([])

function findNode(nodes, id) {
  for (const node of nodes) {
    if (node.id === id) return node
    if (node.children?.length) {
      const found = findNode(node.children, id)
      if (found) return found
    }
  }
  return null
}

const breadcrumb = computed(() => path.value.map((id) => findNode(props.tree, id)).filter(Boolean))

const currentChildren = computed(() => {
  if (!path.value.length) return props.tree
  const current = breadcrumb.value[breadcrumb.value.length - 1]
  return current?.children ?? []
})

const currentParentId = computed(() =>
  path.value.length ? path.value[path.value.length - 1] : null,
)

function drillInto(node) {
  path.value.push(node.id)
}

function goToBreadcrumb(index) {
  path.value = path.value.slice(0, index + 1)
}

function goToRoot() {
  path.value = []
}
</script>

<template>
  <div>
    <div class="mb-3 flex flex-wrap items-center gap-1 text-sm">
      <button
        type="button"
        class="font-medium"
        :class="path.length === 0 ? 'text-gray-900' : 'text-indigo-600 hover:underline'"
        @click="goToRoot"
      >
        Alle Orte
      </button>
      <template v-for="(crumb, index) in breadcrumb" :key="crumb.id">
        <span class="text-gray-300">/</span>
        <button
          type="button"
          class="font-medium"
          :class="
            index === breadcrumb.length - 1 ? 'text-gray-900' : 'text-indigo-600 hover:underline'
          "
          @click="goToBreadcrumb(index)"
        >
          {{ crumb.name }}
        </button>
      </template>
    </div>

    <div class="space-y-2">
      <div
        v-for="node in currentChildren"
        :key="node.id"
        class="flex items-center gap-2 rounded-xl border border-gray-200 bg-white p-3 shadow-sm"
      >
        <button
          type="button"
          class="flex min-w-0 flex-1 items-center gap-2 text-left"
          @click="drillInto(node)"
        >
          <span class="text-lg">📦</span>
          <span class="min-w-0 flex-1">
            <span class="block truncate text-sm font-medium text-gray-900">{{ node.name }}</span>
            <span v-if="node.description" class="block truncate text-xs text-gray-500">{{
              node.description
            }}</span>
          </span>
          <span v-if="node.children?.length" class="shrink-0 text-xs text-gray-400">
            {{ node.children.length }} Unterort{{ node.children.length === 1 ? '' : 'e' }}
          </span>
        </button>
        <button
          v-if="canEdit"
          type="button"
          class="shrink-0 rounded-lg p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
          @click="emit('edit', node)"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
            />
          </svg>
        </button>
        <button
          v-if="canEdit"
          type="button"
          class="shrink-0 rounded-lg p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
          @click="emit('delete', node)"
        >
          <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
            />
          </svg>
        </button>
      </div>

      <p v-if="!currentChildren.length" class="py-6 text-center text-sm text-gray-400">
        Keine Orte vorhanden.
      </p>
    </div>

    <button
      v-if="canEdit"
      type="button"
      class="mt-4 w-full rounded-lg border border-dashed border-indigo-300 py-2.5 text-sm font-medium text-indigo-600 hover:bg-indigo-50"
      @click="emit('add', currentParentId)"
    >
      + Ort hier hinzufügen
    </button>
  </div>
</template>
