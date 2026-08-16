<script setup lang="ts">
const route = useRoute()
await navigateTo({ path: '/get', query: route.query }, { redirectCode: 301 })
</script>

<template>
  <div />
</template>
