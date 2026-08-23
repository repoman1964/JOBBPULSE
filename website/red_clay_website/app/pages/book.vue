<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string

useSeoMeta({
  title: 'Book an estimate | Red Clay',
  description: 'Book a painting estimate in metro Atlanta. Call or use the calendar when it is connected.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Book</p>
        <h1 class="page-hero__title">Book an estimate</h1>
        <p class="section__lead">
          Prefer the phone?
          <a :href="`tel:${phoneTel}`">{{ phone }}</a>
          — a person answers during business hours.
        </p>
      </div>
    </section>
    <section class="section">
      <div class="container">
        <!-- Operator: paste the GoHighLevel calendar embed inside #ghl-calendar. -->
        <div id="ghl-calendar" data-ghl-embed></div>
        <p class="muted" style="margin-top: 1.5rem">
          Calendar mounts here when the booking embed is added. Until then, call
          <a :href="`tel:${phoneTel}`">{{ phone }}</a>
          or use the
          <NuxtLink to="/contact">contact form</NuxtLink>.
        </p>
      </div>
    </section>
  </div>
</template>
