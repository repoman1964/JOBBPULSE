<script setup lang="ts">
const route = useRoute()
const q = ref(typeof route.query.q === 'string' ? route.query.q : '')

watch(
  () => route.query.q,
  (value) => {
    if (typeof value === 'string') q.value = value
  },
)

function onSearch() {
  const term = q.value.trim()
  navigateTo(term ? { path: '/search', query: { q: term } } : '/projects')
}
</script>

<template>
  <header class="site-header">
    <div class="container site-header__inner">
      <NuxtLink to="/" class="logo">JobPulse</NuxtLink>
      <nav class="nav" aria-label="Primary">
        <NuxtLink to="/projects">Browse Projects</NuxtLink>
        <NuxtLink to="/services">Services</NuxtLink>
        <NuxtLink to="/locations">Locations</NuxtLink>
        <NuxtLink to="/contractors">Contractors</NuxtLink>
        <NuxtLink to="/how-it-works">How It Works</NuxtLink>
        <NuxtLink to="/for-contractors">For Contractors</NuxtLink>
      </nav>
      <form class="header-search search-bar" @submit.prevent="onSearch">
        <input v-model="q" type="search" name="q" placeholder="Search projects…" aria-label="Search projects" />
        <button class="btn btn-primary" type="submit">Search</button>
      </form>
    </div>
  </header>
</template>
