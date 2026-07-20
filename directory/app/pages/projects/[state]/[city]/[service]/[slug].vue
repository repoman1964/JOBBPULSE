<template>
  <div class="shell">
    <header class="header">
      <NuxtLink to="/" class="wordmark">Job<span>Pulse</span></NuxtLink>
    </header>
    <section class="hero">
      <h1>Project listing</h1>
      <p class="muted">
        {{ state }} / {{ city }} / {{ service }} / {{ slug }}
      </p>
      <p class="muted">
        Approved Jobs will publish before-and-after project pages here with SEO metadata.
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const state = computed(() => String(route.params.state))
const city = computed(() => String(route.params.city))
const service = computed(() => String(route.params.service))
const slug = computed(() => String(route.params.slug))

useSeoMeta({
  title: () => `${slug.value} | ${service.value} project | JobPulse`,
  description: 'Completed project proof on JobPulse local directory',
})
</script>
