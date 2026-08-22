<script setup lang="ts">
useSeoMeta({
  title: 'Terms | ABC Painters',
  description: 'Terms of use placeholder for the ABC Painters demo website.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Terms' }]" />
        <h1 class="page-hero__title">Terms</h1>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container legal">
        <p>
          This website describes residential painting services offered by ABC Painters in Acworth, Kennesaw, and
          Cartersville, Georgia. Quotes, schedules, and warranties are confirmed in writing after a site visit — not
          by this page alone.
        </p>
        <p>
          This page is placeholder legal copy for a demo marketing site. Replace it with counsel-reviewed terms before
          using the site with real customers.
        </p>
        <p>Contact: (555) 123-4567 · painter@abcpainters.com</p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.legal {
  max-width: 40rem;
}
</style>
