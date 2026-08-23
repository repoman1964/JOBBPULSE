<script setup lang="ts">
import type { CarouselJob } from '~/utils/demoProjects'

defineProps<{ jobs: CarouselJob[] }>()
</script>

<template>
  <div class="carousel" role="list">
    <NuxtLink
      v-for="job in jobs"
      :key="job.slug"
      class="project-card"
      :to="`/work/${job.slug}`"
      role="listitem"
    >
      <img
        :src="job.primaryImageUrl || '/images/exterior.jpg'"
        :alt="job.publicTitle"
        width="800"
        height="450"
      />
      <div class="project-card__body">
        <p class="section__eyebrow">{{ job.city }} · {{ job.serviceType }}</p>
        <h3>{{ job.publicTitle }}</h3>
        <p>{{ job.publicSummary }}</p>
      </div>
    </NuxtLink>
  </div>
</template>
