<script setup lang="ts">
import { TRUST_CHIPS } from '~/utils/siteContent'

useSeoMeta({
  title: 'About Red Clay',
  description:
    'Metro Atlanta painters. Exterior-led, licensed and insured, written estimates. A local crew — not a call center.',
})
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">About</p>
        <h1 class="page-hero__title">A painting crew that treats prep as the job.</h1>
        <p class="section__lead">
          Red Clay is named for the ground under metro Atlanta houses. We paint exteriors first. Interiors when they
          fit. Licensed, insured, and local.
        </p>
      </div>
    </section>
    <section class="section">
      <div class="container silo-layout">
        <div>
          <h2>How we work</h2>
          <p>
            Owner Jordan Hale built the company around a simple rule: do not roll over failed paint and call it a
            warranty job. We scrape, prime, and write the number before a brush hits the house.
          </p>
          <p>
            The crew is directly employed. We work Atlanta, Decatur, Marietta, Roswell, Sandy Springs, and Brookhaven.
            If something is not right, tell us — we come back.
          </p>
          <ul class="chips">
            <li v-for="c in TRUST_CHIPS" :key="c">{{ c }}</li>
          </ul>
        </div>
        <img src="/images/crew.jpg" alt="Red Clay crew working an exterior" width="800" height="600" />
      </div>
    </section>
  </div>
</template>
