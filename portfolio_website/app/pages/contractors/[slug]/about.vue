<script setup lang="ts">
/** Legacy route: profile content now lives at /contractors/[slug]. */
const route = useRoute()
const slug = String(route.params.slug || '')

await navigateTo(`/contractors/${slug}`, { redirectCode: 301, replace: true })
</script>

<template>
  <div class="container">
    <p class="muted">Redirecting to contractor profile…</p>
  </div>
</template>
