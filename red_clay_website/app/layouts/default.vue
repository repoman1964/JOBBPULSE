<script setup lang="ts">
const config = useRuntimeConfig()
const phoneTel = config.public.phoneTel as string
</script>

<template>
  <div class="site">
    <SiteHeader />
    <main class="site-main">
      <slot />
    </main>
    <SiteFooter />
    <div class="mobile-cta" aria-label="Quick actions">
      <a class="btn btn--secondary" :href="`tel:${phoneTel}`">Call</a>
      <NuxtLink class="btn btn--primary" to="/contact">Free estimate</NuxtLink>
    </div>
  </div>
</template>
