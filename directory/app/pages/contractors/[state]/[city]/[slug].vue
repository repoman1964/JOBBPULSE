<template>
  <div class="shell">
    <header class="header">
      <NuxtLink to="/" class="wordmark">Job<span>Pulse</span></NuxtLink>
    </header>
    <section class="hero">
      <h1>Contractor profile</h1>
      <p class="muted">
        {{ state }} / {{ city }} / {{ slug }}
      </p>
      <p class="muted">
        Public contractor pages will render company profile, services, gallery, and lead form here.
      </p>
    </section>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const state = computed(() => String(route.params.state))
const city = computed(() => String(route.params.city))
const slug = computed(() => String(route.params.slug))

useSeoMeta({
  title: () => `${slug.value} | JobPulse Directory`,
  description: 'Contractor profile on JobPulse local directory',
})
</script>
