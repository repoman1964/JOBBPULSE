<script setup lang="ts">
const config = useRuntimeConfig()

useSeoMeta({
  title: 'For Contractors | JobPulse',
  description: 'Turn completed jobs into a living public portfolio and inbound leads.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <h1>For contractors</h1>
      <p>
        Finish the job. Document it in JobPulse. Your public portfolio grows automatically with real visual proof.
      </p>
    </section>

    <div class="panel">
      <h2>Why publish completed projects?</h2>
      <ul>
        <li>Homeowners browse work first — your photos do the selling.</li>
        <li>Each project page can generate attributed leads.</li>
        <li>Service and city pages surface your inventory without thin keyword pages.</li>
      </ul>
      <div class="cta-actions">
        <a class="btn btn-primary" :href="String(config.public.contractorAppUrl)" rel="noopener">
          Open contractor app
        </a>
        <NuxtLink class="btn btn-secondary" to="/projects">See live projects</NuxtLink>
      </div>
    </div>
  </div>
</template>
