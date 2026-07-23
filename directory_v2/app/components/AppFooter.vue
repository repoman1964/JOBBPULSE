<script setup lang="ts">
const config = useRuntimeConfig()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div>
        <strong>JobPulse</strong>
        <p class="muted">
          A living local portfolio of real work completed by local contractors.
        </p>
      </div>
      <div>
        <strong>Explore</strong>
        <p><NuxtLink to="/projects">Projects</NuxtLink></p>
        <p><NuxtLink to="/services">Services</NuxtLink></p>
        <p><NuxtLink to="/locations">Locations</NuxtLink></p>
      </div>
      <div>
        <strong>Contractors</strong>
        <p><NuxtLink to="/for-contractors">Join JobPulse</NuxtLink></p>
        <p>
          <a :href="String(config.public.contractorAppUrl)" rel="noopener">Contractor app</a>
        </p>
        <p><NuxtLink to="/how-it-works">How it works</NuxtLink></p>
      </div>
    </div>
  </footer>
</template>
