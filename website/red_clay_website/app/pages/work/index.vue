<script setup lang="ts">
const demo = useDemoProjects()

useSeoMeta({
  title: 'Work | Red Clay',
  description: 'Recent exterior, interior, deck, and trim painting across metro Atlanta.',
})

await demo.fetchLiveList()
const jobs = computed(() => demo.carouselJobs())
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Work</p>
        <h1 class="page-hero__title">Recent projects</h1>
        <p class="section__lead">Before, after, and the posts we wrote from the job. Click through for the full page.</p>
      </div>
    </section>
    <section class="section">
      <div class="container card-grid card-grid--2">
        <NuxtLink v-for="job in jobs" :key="job.slug" class="project-card" :to="`/work/${job.slug}`">
          <img :src="job.primaryImageUrl || '/images/exterior.jpg'" :alt="job.publicTitle" width="800" height="450" />
          <div class="project-card__body">
            <p class="section__eyebrow">{{ job.city }} · {{ job.serviceType }}</p>
            <h3>{{ job.publicTitle }}</h3>
            <p>{{ job.publicSummary }}</p>
          </div>
        </NuxtLink>
      </div>
    </section>
  </div>
</template>
