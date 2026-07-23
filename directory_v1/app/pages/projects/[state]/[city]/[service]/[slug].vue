<template>
  <div class="shell">
    <header class="header">
      <NuxtLink to="/" class="wordmark">Job<span>Pulse</span></NuxtLink>
      <span class="muted" style="font-size: 13px;">Project</span>
    </header>

    <section v-if="pending" class="hero">
      <p class="muted">Loading project…</p>
    </section>

    <section v-else-if="project" class="hero project">
      <p class="muted meta-line">
        {{ locationLine }}
        <template v-if="project.service_key"> · {{ formatService(project.service_key) }}</template>
      </p>
      <h1>{{ project.public_title }}</h1>
      <p class="summary">{{ project.public_summary }}</p>

      <div v-if="afters.length || befores.length" class="gallery">
        <div v-if="afters.length" class="gallery-block">
          <h2>After</h2>
          <div class="thumbs">
            <a
              v-for="m in afters"
              :key="m.id"
              :href="m.url || undefined"
              target="_blank"
              rel="noopener"
              class="thumb"
            >
              <img v-if="m.url" :src="m.url" :alt="'After photo'" loading="lazy" />
              <span v-else class="muted">Image unavailable</span>
            </a>
          </div>
        </div>
        <div v-if="befores.length" class="gallery-block">
          <h2>Before</h2>
          <div class="thumbs">
            <a
              v-for="m in befores"
              :key="m.id"
              :href="m.url || undefined"
              target="_blank"
              rel="noopener"
              class="thumb"
            >
              <img v-if="m.url" :src="m.url" :alt="'Before photo'" loading="lazy" />
              <span v-else class="muted">Image unavailable</span>
            </a>
          </div>
        </div>
      </div>

      <div v-if="project.contractor?.company_name" class="contractor-card">
        <div>
          <div class="muted" style="font-size: 12px;">Contractor</div>
          <strong>{{ project.contractor.company_name }}</strong>
          <div v-if="project.contractor.headline" class="muted" style="font-size: 13px;">
            {{ project.contractor.headline }}
          </div>
        </div>
        <NuxtLink
          v-if="project.contractor.public_path"
          :to="project.contractor.public_path"
          class="btn-link"
        >
          View profile
        </NuxtLink>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const slug = computed(() => String(route.params.slug))
const api = usePublicApi()

const { data: project, pending, error } = await useAsyncData(
  () => `project-${slug.value}`,
  async () => {
    try {
      return await api.getProject(slug.value)
    } catch (e: any) {
      throw createError({
        statusCode: e?.statusCode || 404,
        statusMessage: e?.statusMessage || 'Project not found',
      })
    }
  },
)

if (error.value && !project.value) {
  throw createError({
    statusCode: 404,
    statusMessage: 'Project not found or no longer published',
  })
}

const afters = computed(() =>
  (project.value?.media || [])
    .filter((m) => m.stage_label === 'after')
    .sort((a, b) => a.display_order - b.display_order),
)
const befores = computed(() =>
  (project.value?.media || [])
    .filter((m) => m.stage_label === 'before')
    .sort((a, b) => a.display_order - b.display_order),
)

const locationLine = computed(() => {
  if (!project.value) return ''
  return (
    project.value.location_display ||
    [project.value.city, project.value.state].filter(Boolean).join(', ') ||
    'Local project'
  )
})

function formatService(key: string) {
  return key.replace(/_/g, ' ')
}

useSeoMeta({
  title: () => project.value?.seo_title || project.value?.public_title || 'Project | JobPulse',
  description: () =>
    project.value?.seo_description ||
    project.value?.public_summary?.slice(0, 160) ||
    'Completed project on JobPulse local directory',
  ogTitle: () => project.value?.public_title || 'Project',
  ogDescription: () => project.value?.public_summary?.slice(0, 160) || '',
})

useHead(() => {
  const ld = project.value?.structured_data_json
  if (!ld) return {}
  return {
    script: [
      {
        type: 'application/ld+json',
        children: JSON.stringify(ld),
      },
    ],
  }
})
</script>

<style scoped>
.project h1 {
  margin: 4px 0 12px;
}
.meta-line {
  margin: 0;
  font-size: 13px;
  text-transform: capitalize;
}
.summary {
  white-space: pre-wrap;
  line-height: 1.6;
  margin: 0 0 24px;
}
.gallery {
  display: flex;
  flex-direction: column;
  gap: 20px;
  margin-bottom: 24px;
}
.gallery h2 {
  font-size: 0.95rem;
  margin: 0 0 8px;
}
.thumbs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 10px;
}
.thumb {
  display: block;
  aspect-ratio: 4/3;
  border-radius: 10px;
  overflow: hidden;
  border: 1px solid var(--jp-border);
  background: #f1f5f9;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.contractor-card {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 14px 16px;
  border: 1px solid var(--jp-border);
  border-radius: 12px;
  background: #f8fafc;
}
.btn-link {
  font-weight: 600;
  font-size: 14px;
  white-space: nowrap;
}
</style>
