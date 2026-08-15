<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

const api = usePublicApi()

const { data, error } = await useAsyncData('home', () => api.getHome())

const { data: filterData } = await useAsyncData('home-filters', async () => {
  const [services, locations, contractors] = await Promise.all([
    api.listServices().catch(() => ({ items: [] as any[] })),
    api.listLocations().catch(() => ({ items: [] as any[] })),
    api.listContractors({ limit: 50 }).catch(() => ({ items: [] as any[] })),
  ])
  return { services, locations, contractors }
})

const serviceOptions = computed(() =>
  (filterData.value?.services?.items || []).map((s: any) => ({
    value: s.service_key || s.slug,
    label: s.name,
    to: s.public_path || `/services/${s.slug}`,
  })),
)

const locationOptions = computed(() =>
  (filterData.value?.locations?.items || []).map((l: any) => ({
    value: l.slug,
    // Metro-scoped directory: city only, never state
    label: cityOnly(l.city, l.name),
    to: l.public_path || `/locations/${l.slug}`,
  })),
)

const contractorOptions = computed(() =>
  (filterData.value?.contractors?.items || []).map((c: any) => ({
    value: c.slug,
    label: c.company_name,
    to: c.public_path || `/contractors/${c.slug}`,
  })),
)

/** Premium placements — max two each */
const featuredProjects = computed(() => (data.value?.featured_projects || []).slice(0, 2))
const featuredContractors = computed(() => (data.value?.featured_contractors || []).slice(0, 2))

useSeoMeta({
  title: 'JobPulse — Browse real local projects',
  description: 'Browse real projects completed by local contractors. Work first, then connect.',
})
</script>

<template>
  <div class="home">
    <!-- Above the fold: headline, sub, filters, carousel — fills viewport under header -->
    <div class="home-above-fold">
      <h1 class="home-hero__title home-above-fold__title">
        Browse real projects completed by local contractors
      </h1>
      <p class="home-hero__sub home-above-fold__sub">
        Filter by service, location, or contractor to see finished work near you.
      </p>
      <div class="home-above-fold__filters">
        <HomeFilterPills
          :services="serviceOptions"
          :locations="locationOptions"
          :contractors="contractorOptions"
        />
      </div>

      <p v-if="error" class="container empty home-above-fold__error">
        Could not load projects. Is the API running on port 8000?
      </p>

      <div v-if="data" class="home-above-fold__carousel container container--carousel">
        <h2 class="section__title section__title--carousel">Recently completed projects</h2>
        <ProjectCarousel
          :projects="data.recent_projects || []"
          empty-text="No published projects yet. Seed demo data or publish from the contractor app."
        />
      </div>
    </div>

    <!-- Below the fold -->
    <section
      v-if="data && (featuredProjects.length || featuredContractors.length)"
      class="section home-section home-section--featured"
    >
      <div class="container container--carousel featured-split">
        <div v-if="featuredProjects.length" class="featured-split__col">
          <h2 class="section__title">Featured projects</h2>
          <div class="featured-project-grid">
            <HomeProjectCard
              v-for="project in featuredProjects"
              :key="project.id || project.slug"
              :project="project"
            />
          </div>
        </div>
        <div v-if="featuredContractors.length" class="featured-split__col">
          <h2 class="section__title">Featured contractors</h2>
          <div class="featured-contractor-grid">
            <HomeContractorCard
              v-for="c in featuredContractors"
              :key="c.slug"
              :contractor="c"
            />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>
