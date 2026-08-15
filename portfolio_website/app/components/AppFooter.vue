<script setup lang="ts">
const config = useRuntimeConfig()
</script>

<template>
  <footer class="site-footer">
    <div class="container site-footer__grid">
      <div class="site-footer__brand">
        <strong class="site-footer__logo">JobPulse</strong>
        <p class="muted">
          A living local portfolio of real work completed by Metro Atlanta contractors.
        </p>
      </div>
      <div>
        <strong>Explore</strong>
        <p><NuxtLink to="/projects">Projects</NuxtLink></p>
        <p><NuxtLink to="/services">Services</NuxtLink></p>
        <p><NuxtLink to="/locations">Locations</NuxtLink></p>
        <p><NuxtLink to="/contractors">Contractors</NuxtLink></p>
      </div>
      <div>
        <strong>Contractors</strong>
        <p><NuxtLink to="/for-contractors">Join JobPulse</NuxtLink></p>
        <p>
          <a :href="String(config.public.contractorAppUrl)" rel="noopener">Contractor app</a>
        </p>
        <p><NuxtLink to="/how-it-works">How it works</NuxtLink></p>
      </div>
      <div>
        <strong>Legal</strong>
        <p><span class="muted">Privacy</span></p>
        <p><span class="muted">Terms</span></p>
      </div>
      <div>
        <strong>Contact</strong>
        <p><a href="mailto:hello@jobpulse.local">hello@jobpulse.local</a></p>
      </div>
    </div>
  </footer>
</template>
