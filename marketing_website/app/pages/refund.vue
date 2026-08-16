<script setup lang="ts">
import { offer, publishingPromise, workGuarantee } from '~/data/offer'

const config = useRuntimeConfig()
const email = config.public.contactEmail as string

useSeoMeta({
  title: 'Guarantees | JobbPulse',
  description: `${offer.guaranteeTitle} and ${offer.promiseTitle}.`,
})
</script>

<template>
  <article class="container legal">
    <h1>Guarantees</h1>
    <p class="muted">This is our refund and service-promise policy.</p>

    <h2>{{ workGuarantee.title }}</h2>
    <p v-for="(line, index) in workGuarantee.paragraphs" :key="`work-${index}`">
      <strong v-if="line.emphasize">{{ line.text }}</strong>
      <template v-else>{{ line.text }}</template>
    </p>

    <h2>{{ publishingPromise.title }}</h2>
    <p v-for="(line, index) in publishingPromise.paragraphs" :key="`pub-${index}`">
      <strong v-if="line.emphasize">{{ line.text }}</strong>
      <template v-else>{{ line.text }}</template>
    </p>

    <p>
      Questions? Write
      <a :href="`mailto:${email}`">{{ email }}</a>.
    </p>
  </article>
</template>
