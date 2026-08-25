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
      <div class="container">
        <ProjectCarousel :jobs="jobs" />
      </div>
    </section>
  </div>
</template>
