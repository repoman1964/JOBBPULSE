<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()
const slug = computed(() => String(route.params.slug || ''))

const { data, error } = await useAsyncData(
  () => `contractor-about-${slug.value}`,
  () => api.getContractor(slug.value, { project_limit: 6 }),
  { watch: [slug] },
)

if (error.value) {
  throw createError({ statusCode: 404, statusMessage: 'Contractor not found' })
}

const contractor = computed(() => data.value)

useSeoMeta({
  title: () => `About ${contractor.value?.company_name || 'contractor'} | JobPulse`,
  description: () => contractor.value?.public_description || '',
})
</script>

<template>
  <div v-if="contractor" class="container">
    <section class="page-hero">
      <ProjectBreadcrumbs
        :items="[
          { label: 'Home', to: '/' },
          { label: 'Contractors', to: '/contractors' },
          { label: contractor.company_name, to: `/contractors/${contractor.slug}` },
          { label: 'About' },
        ]"
      />
      <h1>About {{ contractor.company_name }}</h1>
      <p v-if="contractor.headline" class="muted">{{ contractor.headline }}</p>
    </section>

    <div class="two-col">
      <div class="panel">
        <h2>Company story</h2>
        <p style="white-space: pre-wrap">
          {{ contractor.public_description || 'This contractor has not added a full about section yet.' }}
        </p>
        <h3>Services</h3>
        <ul>
          <li v-for="s in contractor.services || []" :key="s.service_key">{{ s.display_name }}</li>
        </ul>
        <h3>Areas served</h3>
        <ul>
          <li v-for="(a, i) in contractor.service_areas || []" :key="i">
            {{ a.display_name || a.city }}
          </li>
        </ul>
        <p v-if="contractor.website_url">
          <a :href="contractor.website_url" rel="noopener" target="_blank">Website</a>
        </p>
        <p v-if="contractor.contact_phone">Phone: {{ contractor.contact_phone }}</p>
        <div class="cta-actions">
          <NuxtLink class="btn btn-primary" :to="`/contractors/${contractor.slug}`">
            View project portfolio
          </NuxtLink>
        </div>
      </div>
      <aside>
        <LeadForm
          v-if="contractor.lead_form_enabled !== false"
          :contractor-slug="contractor.slug"
          source-page-type="contractor_about"
          headline="Request an estimate"
        />
        <section v-if="contractor.recent_projects?.length" class="section">
          <h2 class="section__title">Recent projects</h2>
          <ProjectGallery :projects="contractor.recent_projects" />
        </section>
      </aside>
    </div>
  </div>
</template>
