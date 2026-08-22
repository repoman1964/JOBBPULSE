<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

const ESTIMATE_TAB = 'estimate' as const

const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

/** 'all' | service_key | 'estimate' — estimate is always last in the tab list */
const activeTab = ref<string>('all')
/** Service key used only for project list queries (never the estimate tab). */
const serviceFilter = ref('')
const pageSize = 12
const offset = ref(0)
const loadingMore = ref(false)

const isEstimateTab = computed(() => activeTab.value === ESTIMATE_TAB)

const { data: contractor, error } = await useAsyncData(
  () => `contractor-portfolio-meta-${slug.value}`,
  () => api.getContractor(slug.value, { project_limit: 12 }),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Contractor not found' })
}

const { data: projectPage, pending } = await useAsyncData(
  () => `contractor-portfolio-projects-${slug.value}-${serviceFilter.value}-${offset.value}`,
  () =>
    api.listProjects({
      contractor_slug: slug.value,
      service_key: serviceFilter.value || undefined,
      limit: pageSize,
      offset: offset.value,
    }),
  { watch: [slug, serviceFilter, offset] },
)

/** Accumulated list for "load more" (resets when filter/slug changes). */
const accumulated = ref<any[]>([])

watch(
  [slug, serviceFilter],
  () => {
    offset.value = 0
    accumulated.value = []
  },
  { flush: 'sync' },
)

watch(
  projectPage,
  (page) => {
    if (!page?.items) return
    if (offset.value === 0) {
      accumulated.value = [...page.items]
    } else {
      const seen = new Set(accumulated.value.map((p) => p.id || p.slug))
      for (const p of page.items) {
        const key = p.id || p.slug
        if (!seen.has(key)) {
          accumulated.value.push(p)
          seen.add(key)
        }
      }
    }
  },
  { immediate: true },
)

const contractorMeta = computed(() => contractor.value)
const projects = computed(() => accumulated.value)

/** Always fill up to 3 cards: featured first, then other projects. Horizontal row, not a carousel. */
const featuredProjects = computed(() => {
  const fromMeta = contractorMeta.value?.recent_projects || []
  const fromList = projects.value || []
  const pool = fromMeta.length ? fromMeta : fromList
  if (!pool.length) return []

  const keyOf = (p: { id?: string; slug?: string }) => p.id || p.slug || ''
  const picked: typeof pool = []
  const seen = new Set<string>()

  for (const p of pool) {
    if (!p.featured) continue
    const k = keyOf(p)
    if (!k || seen.has(k)) continue
    seen.add(k)
    picked.push(p)
    if (picked.length >= 3) return picked
  }
  for (const p of pool) {
    const k = keyOf(p)
    if (!k || seen.has(k)) continue
    seen.add(k)
    picked.push(p)
    if (picked.length >= 3) break
  }
  if (picked.length < 3 && fromList.length) {
    for (const p of fromList) {
      const k = keyOf(p)
      if (!k || seen.has(k)) continue
      seen.add(k)
      picked.push(p)
      if (picked.length >= 3) break
    }
  }
  return picked
})

const servicePills = computed(() => contractorMeta.value?.services || [])

const canLoadMore = computed(() => {
  const page = projectPage.value
  if (!page?.items) return false
  return page.items.length >= pageSize
})

const areaLabel = computed(() => {
  const areas = contractorMeta.value?.service_areas || []
  if (!areas.length) return ''
  return areas
    .map((a) => cityOnly(a.city, a.display_name))
    .filter(Boolean)
    .join(', ')
})

const profilePath = computed(
  () => contractorMeta.value?.public_path || `/contractors/${slug.value}`,
)

const leadFormEnabled = computed(() => contractorMeta.value?.lead_form_enabled !== false)

function setServiceTab(key: string) {
  activeTab.value = key || 'all'
  serviceFilter.value = key || ''
}

function setEstimateTab() {
  activeTab.value = ESTIMATE_TAB
}

function onTabChange(key: string) {
  if (key === ESTIMATE_TAB) {
    setEstimateTab()
    return
  }
  setServiceTab(key === 'all' ? '' : key)
}

function loadMore() {
  if (!canLoadMore.value || loadingMore.value || pending.value) return
  loadingMore.value = true
  offset.value += pageSize
}

watch(pending, (isPending) => {
  if (!isPending) loadingMore.value = false
})

useSeoMeta({
  title: () =>
    `${contractorMeta.value?.company_name || 'Contractor'} portfolio | JobPulse`,
  description: () =>
    contractorMeta.value?.seo_description ||
    contractorMeta.value?.headline ||
    `Documented projects by ${contractorMeta.value?.company_name || 'this contractor'}.`,
})
</script>

<template>
  <div v-if="contractorMeta" class="container contractor-portfolio">
    <section class="page-hero contractor-portfolio__hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Contractors', to: '/contractors' },
          { label: contractorMeta.company_name, to: profilePath },
          { label: 'Portfolio' },
        ]"
      />
      <div class="contractor-portfolio__hero-row">
        <div>
          <h1>{{ contractorMeta.company_name }}</h1>
          <p v-if="areaLabel" class="contractor-portfolio__subline">
            Serving {{ areaLabel }}
          </p>
          <p v-if="contractorMeta.headline" class="contractor-portfolio__subline">
            {{ contractorMeta.headline }}
          </p>
        </div>
        <div class="cta-actions">
          <NuxtLink class="btn btn-secondary" :to="profilePath">About</NuxtLink>
          <a
            v-if="contractorMeta.contact_phone"
            class="btn btn-primary"
            :href="`tel:${contractorMeta.contact_phone}`"
          >
            Call
          </a>
        </div>
      </div>
    </section>

    <section v-if="featuredProjects.length" class="section contractor-portfolio__featured">
      <h2 class="section__title">Featured projects</h2>
      <div class="contractor-portfolio__featured-row">
        <HomeProjectCard
          v-for="p in featuredProjects"
          :key="p.id || p.slug"
          :project="p"
          :show-contractor="false"
        />
      </div>
    </section>

    <section class="section contractor-portfolio__all">
      <div class="contractor-portfolio__all-head">
        <h2 class="section__title">All projects</h2>
      </div>

      <ExpertiseTabs
        :model-value="activeTab"
        :services="servicePills"
        :show-estimate="leadFormEnabled"
        @update:model-value="onTabChange"
      />

      <div v-if="isEstimateTab" class="contractor-portfolio__estimate-panel">
        <LeadForm
          :contractor-slug="contractorMeta.slug"
          source-page-type="contractor_portfolio"
          headline="Request an estimate"
        />
      </div>

      <template v-else>
        <p v-if="pending && !projects.length" class="muted">Loading projects…</p>

        <ProjectGallery
          v-else
          :projects="projects"
          :show-contractor="false"
          :show-before-after-badge="false"
          compact
          empty-text="This contractor has not published projects yet."
        />

        <div v-if="canLoadMore" class="contractor-portfolio__load-more">
          <button
            type="button"
            class="btn btn-secondary"
            :disabled="loadingMore || pending"
            @click="loadMore"
          >
            {{ loadingMore ? 'Loading…' : 'Load more projects' }}
          </button>
        </div>
      </template>
    </section>
  </div>
</template>

<style scoped>
.contractor-portfolio {
  padding-bottom: 2.5rem;
}

.contractor-portfolio__hero-row {
  display: flex;
  flex-wrap: wrap;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem 1.5rem;
}

.contractor-portfolio__hero-row h1 {
  margin: 0 0 0.35rem;
  text-align: left;
}

.contractor-portfolio__subline {
  margin: 0.35rem 0 0;
  color: var(--muted);
  max-width: 36rem;
}

.contractor-portfolio__all {
  margin-top: 1.75rem;
  padding-top: 0;
}

.contractor-portfolio__all-head {
  margin: 0 0 0.75rem;
}

.contractor-portfolio__all-head .section__title {
  margin: 0;
  line-height: 1.25;
}

/* Fixed 3-up horizontal row (not a carousel). Fewer than 3 still left-aligns. */
.contractor-portfolio__featured-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1rem;
  align-items: stretch;
}

.contractor-portfolio__featured-row :deep(.home-project-card) {
  width: 100%;
  max-width: none;
  height: 100%;
  min-width: 0;
}

@media (max-width: 899px) {
  .contractor-portfolio__featured-row {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 559px) {
  .contractor-portfolio__featured-row {
    grid-template-columns: 1fr;
  }
}

.contractor-portfolio__all :deep(.expertise-tabs) {
  margin-bottom: 1.25rem;
}

.contractor-portfolio__estimate-panel {
  max-width: 32rem;
}

.contractor-portfolio__estimate-panel :deep(.lead-form) {
  margin: 0;
}

.contractor-portfolio__estimate-panel :deep(.lead-form h3) {
  margin-top: 0;
}

.contractor-portfolio__load-more {
  display: flex;
  justify-content: center;
  margin-top: 1.25rem;
}
</style>
