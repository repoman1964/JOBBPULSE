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
    <CtaBand />
    <SiteFooter />
    <div class="mobile-cta" aria-label="Quick actions">
      <a class="btn btn--primary" :href="`tel:${phoneTel}`">Call</a>
      <NuxtLink class="btn btn--secondary" to="/contact">Free estimate</NuxtLink>
    </div>
  </div>
</template>
