<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

const titles = {
  home: 'Übersicht',
  items: 'Kabel',
  'item-add': 'Kabel hinzufügen',
  'item-detail': 'Kabel-Details',
  locations: 'Orte',
  settings: 'Einstellungen',
}

const title = computed(() => titles[route.name] ?? 'Home Warehouse')
</script>

<template>
  <header class="sticky top-0 z-20 border-b border-gray-200 bg-white/95 backdrop-blur">
    <div class="flex h-14 items-center justify-center px-4">
      <h1 class="text-base font-semibold text-gray-900">{{ title }}</h1>
    </div>
  </header>
</template>
