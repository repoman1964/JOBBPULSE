<script setup lang="ts">
useSeoMeta({
  title: 'Privacy | ABC Painters',
  description: 'Privacy policy placeholder for the ABC Painters demo website.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <AppBreadcrumbs :items="[{ label: 'Home', to: '/' }, { label: 'Privacy' }]" />
        <h1 class="page-hero__title">Privacy</h1>
      </div>
    </section>
    <section class="section section--tight">
      <div class="container legal">
        <p>
          ABC Painters (4321 Northeast Flanders, Acworth, GA 30101) collects name, phone, email, and project details
          you submit on this site so we can respond to estimate requests. We do not sell that information.
        </p>
        <p>
          This page is placeholder legal copy for a demo marketing site. Replace it with counsel-reviewed language
          before using the site with real customers.
        </p>
        <p>Questions: <a href="mailto:painter@abcpainters.com">painter@abcpainters.com</a></p>
      </div>
    </section>
  </div>
</template>

<style scoped>
.legal {
  max-width: 40rem;
}
</style>
