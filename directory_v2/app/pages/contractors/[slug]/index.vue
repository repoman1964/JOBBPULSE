<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `contractor-${slug.value}`,
  () => api.getContractor(slug.value),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Contractor not found' })
}

const contractor = computed(() => data.value)

useSeoMeta({
  title: () =>
    contractor.value?.seo_title ||
    `${contractor.value?.company_name || 'Contractor'} portfolio | JobPulse`,
  description: () =>
    contractor.value?.seo_description ||
    contractor.value?.public_description ||
    `Documented projects by ${contractor.value?.company_name || 'this contractor'}.`,
})

const areaLabel = computed(() => {
  const areas = contractor.value?.service_areas || []
  if (!areas.length) return ''
  return areas.map((a) => a.display_name || a.city).filter(Boolean).join(', ')
})
</script>

<template>
  <div v-if="contractor" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Contractors', to: '/contractors' },
          { label: contractor.company_name },
        ]"
      />
      <h1>{{ contractor.company_name }}</h1>
      <p class="muted">
        {{ contractor.project_count ?? contractor.recent_projects?.length ?? 0 }} documented projects
        <span v-if="areaLabel"> · Serving {{ areaLabel }}</span>
      </p>
      <p v-if="contractor.headline">{{ contractor.headline }}</p>
      <div class="cta-actions">
        <NuxtLink class="btn btn-secondary" :to="`/contractors/${contractor.slug}/about`">
          About
        </NuxtLink>
        <a
          v-if="contractor.contact_phone"
          class="btn btn-primary"
          :href="`tel:${contractor.contact_phone}`"
        >
          Call
        </a>
      </div>
    </section>

    <div class="two-col">
      <div>
        <section class="section">
          <h2 class="section__title">Project portfolio</h2>
          <ProjectGallery
            :projects="contractor.recent_projects || []"
            empty-text="This contractor has not published projects yet."
          />
        </section>
      </div>
      <aside>
        <div class="panel">
          <h2>Services</h2>
          <ul class="meta-list">
            <li v-for="s in contractor.services || []" :key="s.service_key">
              <NuxtLink :to="`/services/${s.slug || s.service_key}`">{{ s.display_name }}</NuxtLink>
            </li>
          </ul>
          <p v-if="!(contractor.services?.length)" class="muted">Services listed with projects.</p>
        </div>
        <div style="height: 1rem" />
        <LeadForm
          v-if="contractor.lead_form_enabled !== false"
          :contractor-slug="contractor.slug"
          source-page-type="contractor"
          headline="Request an estimate"
        />
      </aside>
    </div>
  </div>
</template>
