<script setup lang="ts">
useSeoMeta({
  title: 'How It Works | JobPulse',
  description: 'How homeowners discover real local work and how contractors publish projects.',
})
</script>

<template>
  <div class="container">
    <section class="page-hero">
      <h1>How JobPulse works</h1>
      <p>Work first. Contractor second. Clear next step to request similar work.</p>
    </section>

    <ol class="how-steps" style="padding-left: 0">
      <li>
        <strong>Contractors document completed jobs</strong>
        <p class="muted">Before photos, after photos, and a short voice summary from the contractor app.</p>
      </li>
      <li>
        <strong>JobPulse creates a public project page</strong>
        <p class="muted">Readable story, gallery, service, and safe location — no private customer details.</p>
      </li>
      <li>
        <strong>Homeowners browse real work nearby</strong>
        <p class="muted">Filter by service and city, open a project, then request an estimate from that contractor.</p>
      </li>
    </ol>

    <section class="cta-band">
      <h2>Ready to explore?</h2>
      <div class="cta-actions">
        <NuxtLink class="btn btn-primary" to="/projects">Browse projects</NuxtLink>
        <NuxtLink class="btn btn-secondary" to="/for-contractors">For contractors</NuxtLink>
      </div>
    </section>
  </div>
</template>
