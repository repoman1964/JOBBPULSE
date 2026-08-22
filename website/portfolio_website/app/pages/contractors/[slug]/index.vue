<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'
import {
  demoRatingSummary,
  demoReviews,
  demoServiceBlurb,
  demoTrustChips,
} from '~/utils/contractorDemo'

const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `contractor-profile-${slug.value}`,
  () => api.getContractor(slug.value, { project_limit: 6 }),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Contractor not found' })
}

const contractor = computed(() => data.value)

const areaLabel = computed(() => {
  const areas = contractor.value?.service_areas || []
  if (!areas.length) return ''
  return areas
    .map((a) => cityOnly(a.city, a.display_name))
    .filter(Boolean)
    .join(', ')
})

const portfolioPath = computed(
  () =>
    contractor.value?.portfolio_path ||
    `/contractors/${contractor.value?.slug || slug.value}/portfolio`,
)

const featuredProjects = computed(() => {
  const projects = contractor.value?.recent_projects || []
  const featured = projects.filter((p) => p.featured)
  return (featured.length ? featured : projects).slice(0, 3)
})

const trustChips = computed(() =>
  demoTrustChips(contractor.value?.slug || slug.value, contractor.value?.trade),
)

const reviews = computed(() => demoReviews(contractor.value?.slug || slug.value))
const ratingSummary = computed(() => demoRatingSummary(contractor.value?.slug || slug.value))

/** Profile tabs: About us | services… | Request an estimate */
const ABOUT_TAB = 'about' as const
const ESTIMATE_TAB = 'estimate' as const
const activeTab = ref<string>(ABOUT_TAB)
const servicePills = computed(() => contractor.value?.services || [])
const leadFormEnabled = computed(() => contractor.value?.lead_form_enabled !== false)
const isAboutTab = computed(() => activeTab.value === ABOUT_TAB)
const isEstimateTab = computed(() => activeTab.value === ESTIMATE_TAB)

const activeService = computed(() => {
  if (isAboutTab.value || isEstimateTab.value) return null
  return servicePills.value.find((s) => s.service_key === activeTab.value) || null
})

const aboutBlurb = computed(() => {
  const c = contractor.value
  if (!c) return ''
  return (
    c.public_description?.trim() ||
    c.headline?.trim() ||
    `${c.company_name || 'This contractor'} has not added a full about section yet.`
  )
})

const serviceBlurb = computed(() => {
  const c = contractor.value
  const s = activeService.value
  if (!c || !s) return ''
  return demoServiceBlurb(c.company_name || 'This contractor', s.display_name, c.slug, areaLabel.value)
})

const tabPanelTitle = computed(() => {
  if (isAboutTab.value) return 'About us'
  if (activeService.value) return activeService.value.display_name
  return ''
})

const tabPanelBody = computed(() => {
  if (isAboutTab.value) return aboutBlurb.value
  if (activeService.value) return serviceBlurb.value
  return ''
})

function onTabChange(key: string) {
  activeTab.value = key || ABOUT_TAB
}

useSeoMeta({
  title: () =>
    contractor.value?.seo_title ||
    `${contractor.value?.company_name || 'Contractor'} | JobPulse`,
  description: () =>
    contractor.value?.seo_description ||
    contractor.value?.public_description ||
    contractor.value?.headline ||
    `Local contractor profile for ${contractor.value?.company_name || 'this contractor'}.`,
})
</script>

<template>
  <div v-if="contractor" class="container contractor-profile">
    <section class="page-hero contractor-profile__hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Contractors', to: '/contractors' },
          { label: contractor.company_name },
        ]"
      />

      <div class="contractor-profile__hero-row">
        <div class="contractor-profile__identity">
          <ContractorAvatar :name="contractor.company_name" size="md" />
          <div class="contractor-profile__identity-text">
            <h1>{{ contractor.company_name }}</h1>
            <p v-if="contractor.headline" class="contractor-profile__headline">
              {{ contractor.headline }}
            </p>
            <p class="muted contractor-profile__stats">
              <span v-if="areaLabel">Serving {{ areaLabel }} · </span>
              <span class="contractor-profile__rating">
                <span class="contractor-profile__star" aria-hidden="true">★</span>
                {{ ratingSummary.rating.toFixed(1) }}
                <span class="muted">({{ ratingSummary.count }} reviews)</span>
              </span>
            </p>
          </div>
        </div>
        <div class="cta-actions contractor-profile__ctas">
          <NuxtLink class="btn btn-primary" :to="portfolioPath">View Portfolio</NuxtLink>
          <a
            v-if="contractor.contact_phone"
            class="btn btn-secondary"
            :href="`tel:${contractor.contact_phone}`"
          >
            Call
          </a>
        </div>
      </div>

      <ContractorTrustChips :chips="trustChips" />

      <div class="contractor-profile__tabs">
        <ExpertiseTabs
          :model-value="activeTab"
          :services="servicePills"
          :show-estimate="leadFormEnabled"
          :first-tab="{ key: ABOUT_TAB, label: 'About us' }"
          aria-label="About, services, and estimate"
          @update:model-value="onTabChange"
        />
      </div>
    </section>

    <!-- Estimate tab: form only -->
    <div v-if="isEstimateTab" class="contractor-profile__estimate-panel">
      <LeadForm
        :contractor-slug="contractor.slug"
        source-page-type="contractor"
        headline="Request an estimate"
      />
    </div>

    <!-- About us / service blurbs + reviews + featured -->
    <div v-else class="contractor-profile__body">
      <section class="section contractor-profile__tab-panel" :aria-label="tabPanelTitle">
        <h2 class="section__title">{{ tabPanelTitle }}</h2>
        <p class="contractor-profile__blurb">
          {{ tabPanelBody }}
        </p>
      </section>

      <ContractorReviews
        :reviews="reviews"
        :rating="ratingSummary.rating"
        :review-count="ratingSummary.count"
      />

      <section v-if="featuredProjects.length" class="section">
        <div class="contractor-profile__featured-head">
          <h2 class="section__title" style="margin: 0">Featured Projects</h2>
          <NuxtLink class="contractor-profile__portfolio-link" :to="portfolioPath">
            View full portfolio →
          </NuxtLink>
        </div>
        <div class="featured-project-grid contractor-profile__featured">
          <HomeProjectCard
            v-for="p in featuredProjects"
            :key="p.id || p.slug"
            :project="p"
          />
        </div>
        <div class="contractor-profile__featured-cta">
          <NuxtLink class="btn btn-outline" :to="portfolioPath">View full portfolio</NuxtLink>
        </div>
      </section>
    </div>
  </div>
</template>

<style scoped>
.contractor-profile {
  padding-bottom: 2.5rem;
}

.contractor-profile__hero-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem 1.5rem;
}

.contractor-profile__identity {
  display: flex;
  gap: 0.85rem;
  /* Avatar centers against the full name + headline + stats stack */
  align-items: center;
  min-width: 0;
  flex: 1;
}

.contractor-profile__identity-text {
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.contractor-profile__identity h1 {
  margin: 0 0 0.25rem;
}

.contractor-profile__headline {
  margin: 0 0 0.35rem;
  color: var(--text);
  font-size: 1rem;
  max-width: 36rem;
}

.contractor-profile__stats {
  margin: 0;
  font-size: 0.92rem;
}

.contractor-profile__rating {
  white-space: nowrap;
}

.contractor-profile__star {
  color: #f59e0b;
}

.contractor-profile__ctas {
  flex-shrink: 0;
}

/* Tab strip sits under badges, left-aligned */
.contractor-profile__tabs {
  margin-top: 1.15rem;
  width: 100%;
  text-align: left;
}

.contractor-profile__body {
  margin-top: 0.35rem;
}

.contractor-profile__tab-panel {
  margin-top: 1.25rem;
}

.contractor-profile__blurb {
  margin: 0;
  white-space: pre-wrap;
  color: var(--text);
  line-height: 1.55;
  max-width: 42rem;
}

.contractor-profile__estimate-panel {
  max-width: 32rem;
  margin-top: 1.25rem;
}

.contractor-profile__estimate-panel :deep(.lead-form) {
  margin: 0;
}

.contractor-profile__estimate-panel :deep(.lead-form h3) {
  margin-top: 0;
}

.contractor-profile__featured-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin-bottom: 0.95rem;
}

.contractor-profile__portfolio-link {
  font-size: 0.9rem;
  font-weight: 600;
}

/* Profile mockup shows up to 3 teaser cards */
.contractor-profile :deep(.featured-project-grid) {
  grid-template-columns: 1fr;
}

@media (min-width: 560px) {
  .contractor-profile :deep(.featured-project-grid) {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (min-width: 900px) {
  .contractor-profile :deep(.featured-project-grid) {
    grid-template-columns: repeat(3, 1fr);
  }
}

.contractor-profile__featured-cta {
  display: flex;
  justify-content: center;
  margin-top: 1.1rem;
}
</style>
