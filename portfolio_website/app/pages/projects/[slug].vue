<script setup lang="ts">
import { cityOnly } from '~/utils/locationLabel'

const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `project-${slug.value}`,
  () => api.getProject(slug.value),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Project not found' })
}

const project = computed(() => data.value)

useSeoMeta({
  title: () => project.value?.seo_title || project.value?.public_title || 'Project',
  description: () =>
    project.value?.seo_description || project.value?.short_summary || project.value?.public_summary || '',
})

function formatDate(value?: string | null) {
  if (!value) return ''
  return new Date(value).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  })
}
</script>

<template>
  <div v-if="project" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Projects', to: '/projects' },
          { label: project.public_title },
        ]"
      />
      <p class="muted" style="margin-bottom: 0.35rem">
        <span v-if="project.service_name">{{ project.service_name }}</span>
        <span v-if="cityOnly(project.city, project.location_display)"> · {{ cityOnly(project.city, project.location_display) }}</span>
        <span v-if="project.published_at"> · {{ formatDate(project.published_at) }}</span>
      </p>
      <h1>{{ project.public_title }}</h1>
      <p v-if="project.contractor?.company_name">
        Completed by
        <NuxtLink v-if="project.contractor.public_path" :to="project.contractor.public_path">
          {{ project.contractor.company_name }}
        </NuxtLink>
        <span v-else>{{ project.contractor.company_name }}</span>
      </p>
    </section>

    <div class="two-col">
      <div>
        <section class="section">
          <BeforeAfterGallery :media="project.media || []" />
        </section>

        <section class="section panel">
          <h2>Project story</h2>
          <p style="white-space: pre-wrap">{{ project.public_summary }}</p>
        </section>

        <section class="section panel">
          <h2>Project details</h2>
          <ul class="meta-list">
            <li v-if="project.service_name">
              <strong>Service</strong>
              <span>
                <NuxtLink
                  v-if="project.service_slug"
                  :to="`/services/${project.service_slug}`"
                >
                  {{ project.service_name }}
                </NuxtLink>
                <template v-else>{{ project.service_name }}</template>
              </span>
            </li>
            <li v-if="cityOnly(project.city, project.location_display)">
              <strong>Location</strong>
              <span>
                <NuxtLink
                  v-if="project.location_slug"
                  :to="`/locations/${project.location_slug}`"
                >
                  {{ cityOnly(project.city, project.location_display) }}
                </NuxtLink>
                <template v-else>{{ cityOnly(project.city, project.location_display) }}</template>
              </span>
            </li>
            <li v-if="project.published_at">
              <strong>Completed</strong>
              <span>{{ formatDate(project.published_at) }}</span>
            </li>
            <li v-if="project.contractor?.company_name">
              <strong>Contractor</strong>
              <span>{{ project.contractor.company_name }}</span>
            </li>
          </ul>
        </section>
      </div>

      <aside>
        <ContractorSummary :contractor="project.contractor" show-about-link />
        <div style="height: 1rem" />
        <LeadForm
          v-if="project.contractor?.slug && project.contractor.lead_form_enabled !== false"
          :contractor-slug="project.contractor.slug"
          :project-slug="project.slug"
          :service-requested="project.service_key || project.service_name || undefined"
          :project-location="cityOnly(project.city, project.location_display) || undefined"
          source-page-type="project"
          headline="Interested in a project like this?"
        />
      </aside>
    </div>

    <RelatedProjects
      title="More from this contractor"
      :projects="project.related?.same_contractor"
    />
    <RelatedProjects title="Similar projects in this city" :projects="project.related?.same_city" />
    <RelatedProjects title="Similar work in this service" :projects="project.related?.same_service" />
    <RelatedProjects title="Nearby completed projects" :projects="project.related?.nearby" />

    <div class="sticky-cta">
      <div class="container cta-actions">
        <a
          v-if="project.contractor?.contact_phone"
          class="btn btn-primary"
          :href="`tel:${project.contractor.contact_phone}`"
        >
          Call contractor
        </a>
        <a class="btn btn-secondary" href="#lead">Request estimate</a>
      </div>
    </div>
  </div>
</template>
