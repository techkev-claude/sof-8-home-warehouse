<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore, registerAuthInterceptor } from './stores/auth'
import AppHeader from './components/layout/AppHeader.vue'
import BottomNav from './components/layout/BottomNav.vue'

const authStore = useAuthStore()
const route = useRoute()
const ready = ref(false)

registerAuthInterceptor()

onMounted(async () => {
  if (authStore.token && !authStore.user) {
    try {
      await authStore.fetchMe()
    } catch {
      authStore.logout()
    }
  }
  ready.value = true
})
</script>

<template>
  <div v-if="ready" class="min-h-screen bg-gray-50">
    <div class="mx-auto flex min-h-screen max-w-[480px] flex-col bg-gray-50">
      <AppHeader v-if="route.name !== 'login'" />
      <main class="flex-1 pb-20">
        <RouterView />
      </main>
      <BottomNav v-if="route.name !== 'login'" />
    </div>
  </div>
</template>
