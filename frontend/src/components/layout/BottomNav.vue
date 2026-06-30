<script setup>
const tabs = [
  { name: 'home', label: 'Übersicht', path: '/' },
  { name: 'items', label: 'Kabel', path: '/items' },
  { name: 'locations', label: 'Orte', path: '/locations' },
  { name: 'settings', label: 'Einstellungen', path: '/settings' },
]
</script>

<template>
  <nav
    class="fixed bottom-0 left-1/2 z-20 w-full max-w-[480px] -translate-x-1/2 border-t border-gray-200 bg-white"
    style="padding-bottom: env(safe-area-inset-bottom)"
  >
    <div class="grid grid-cols-4">
      <RouterLink
        v-for="tab in tabs"
        :key="tab.name"
        :to="tab.path"
        class="flex flex-col items-center gap-1 py-2 text-xs"
        :class="
          $route.name === tab.name ? 'text-indigo-600 font-semibold' : 'text-gray-500'
        "
      >
        <span
          class="h-2 w-2 rounded-full"
          :class="$route.name === tab.name ? 'bg-indigo-600' : 'bg-transparent'"
        />
        {{ tab.label }}
      </RouterLink>
    </div>
  </nav>
</template>
