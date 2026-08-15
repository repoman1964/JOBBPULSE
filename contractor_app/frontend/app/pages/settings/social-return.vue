<script setup lang="ts">
const route = useRoute()
const api = useApi()

onMounted(async () => {
  try {
    if (api.completeSocialReturn) {
      await api.completeSocialReturn(String(route.query.status || 'connected'))
    }
  } catch {
    // still return to settings
  }
  await navigateTo({ path: '/settings', query: { connected: '1' } })
})
</script>

<template>
  <div>
    <JpHeader :show-menu="false" />
    <main class="app-main">
      <p class="muted">Returning to Settings…</p>
    </main>
  </div>
</template>
