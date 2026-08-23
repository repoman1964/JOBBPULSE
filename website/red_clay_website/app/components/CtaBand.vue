<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
</script>

<template>
  <section class="cta-band">
    <div class="container">
      <p class="section__eyebrow">Ready for a quote?</p>
      <h2>Walk the house. Get a number. Then we paint.</h2>
      <p>Written estimates. Licensed crew. Metro Atlanta exteriors first — interiors when they fit the schedule.</p>
      <a class="cta-band__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
      <div class="cta-band__actions">
        <NuxtLink class="btn btn--primary btn--lg" to="/book">Book an estimate</NuxtLink>
      </div>
    </div>
  </section>
</template>
