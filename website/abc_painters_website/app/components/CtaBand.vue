<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
</script>

<template>
  <section class="cta-band">
    <div class="container">
      <p class="section__eyebrow">Ready to start?</p>
      <h2>Get a written quote before any paint goes on the wall.</h2>
      <p>Free in-home estimate. Directly employed crew. Acworth, Kennesaw, and Cartersville.</p>
      <a class="cta-band__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
      <div class="cta-band__actions">
        <NuxtLink class="btn btn--primary btn--lg" to="/contact">Book a free estimate</NuxtLink>
      </div>
    </div>
  </section>
</template>
