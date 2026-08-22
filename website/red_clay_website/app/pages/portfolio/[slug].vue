<script setup lang="ts">
import type { ProjectDetail } from '~/composables/useJobPulse'
import { FALLBACK_JOBS, FALLBACK_MEDIA, formatRelativeDate, projectImageStyle } from '~/utils/siteContent'

const route = useRoute()
const api = useJobPulse()
const slug = computed(() => String(route.params.slug || ''))

const project = ref<ProjectDetail | null>(null)
const error = ref<string | null>(null)

function isUsableImageUrl(url?: string | null) {
  if (!url) return false
  if (url.includes('/demo/')) return false
  if (url.endsWith('-0.png') || url.endsWith('-1.png')) return false
  return true
}

async function load() {
  error.value = null
  try {
    project.value = await api.getProject(slug.value)
  } catch {
    const fb = FALLBACK_JOBS.find((j) => j.slug === slug.value)
    if (fb) {
      const mediaPaths = FALLBACK_MEDIA[fb.slug]
      project.value = {
        ...fb,
        public_summary: fb.public_summary || fb.short_summary,
        media: mediaPaths
          ? [
              { id: 'before', stage_label: 'before', display_order: 0, url: mediaPaths.before },
              { id: 'after', stage_label: 'after', display_order: 1, url: mediaPaths.after },
            ]
          : [],
      } as ProjectDetail
    } else {
      error.value = 'Project not found.'
      project.value = null
    }
  }
}

await load()

useSeoMeta({
  title: () =>
    project.value ? `${project.value.public_title} | Red Clay` : 'Project | Red Clay',
  description: () =>
    project.value?.short_summary ||
    project.value?.public_summary ||
    'Completed cabinet project by Red Clay Cabinet Installers.',
})

const heroStyle = computed(() => {
  const p = project.value
  if (!p) return {}
  if (isUsableImageUrl(p.primary_image_url)) {
    return {
      backgroundImage: `url(${p.primary_image_url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  const after = p.media?.find((m) => m.stage_label === 'after' && isUsableImageUrl(m.url))
  if (after?.url) {
    return {
      backgroundImage: `url(${after.url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  return { background: projectImageStyle(p.public_title) }
})
</script>

<template>
  <div>
    <div v-if="error" class="container section">
      <p class="form-error">{{ error }}</p>
      <NuxtLink class="btn btn--secondary" to="/portfolio">Back to portfolio</NuxtLink>
    </div>

    <template v-else-if="project">
      <section class="project-hero" :style="heroStyle">
        <div class="project-hero__overlay">
          <div class="container">
            <NuxtLink class="project-hero__back" to="/portfolio">← Portfolio</NuxtLink>
            <p v-if="project.service_name" class="badge">{{ project.service_name }}</p>
            <h1>{{ project.public_title }}</h1>
            <p class="project-hero__meta">
              {{ project.location_display || [project.city, project.state].filter(Boolean).join(', ') }}
              · {{ formatRelativeDate(project.published_at) }}
            </p>
          </div>
        </div>
      </section>

      <section class="section section--tight">
        <div class="container project-layout">
          <article>
            <h2>Project details</h2>
            <p class="project-body">{{ project.public_summary || project.short_summary }}</p>
            <div v-if="project.media?.length" class="project-media">
              <h3>Photos</h3>
              <div class="project-media__grid">
                <figure v-for="m in project.media" :key="m.id" class="project-media__item">
                  <div
                    class="project-media__img"
                    :style="
                      m.url && !m.url.includes('/demo/')
                        ? { backgroundImage: `url(${m.url})`, backgroundSize: 'cover', backgroundPosition: 'center' }
                        : { background: projectImageStyle(project.public_title + m.stage_label) }
                    "
                  />
                  <figcaption>{{ m.stage_label }}</figcaption>
                </figure>
              </div>
            </div>
          </article>
          <aside>
            <div class="side-card">
              <h3>Like this install?</h3>
              <p class="muted">Tell us about your kitchen, bath, or built-in project.</p>
              <NuxtLink class="btn btn--primary" to="/contact">Request estimate</NuxtLink>
              <NuxtLink class="btn btn--secondary" to="/portfolio" style="margin-top: 0.5rem; width: 100%">
                More projects
              </NuxtLink>
            </div>
          </aside>
        </div>
      </section>
    </template>
  </div>
</template>

<style scoped>
.project-hero {
  min-height: 16rem;
  position: relative;
  background: var(--clay-dark);
}

.project-hero__overlay {
  background: linear-gradient(to top, rgba(28, 20, 16, 0.88), rgba(28, 20, 16, 0.35));
  color: #fff;
  padding: 2.5rem 0 2rem;
  min-height: 16rem;
  display: flex;
  align-items: flex-end;
}

.project-hero h1 {
  color: #fff;
  font-size: clamp(1.6rem, 3vw, 2.2rem);
  margin: 0.5rem 0 0.35rem;
}

.project-hero__back {
  color: #f3c9b4;
  font-weight: 700;
  font-size: 0.88rem;
  text-decoration: none !important;
}

.project-hero__meta {
  margin: 0;
  color: rgba(255, 245, 238, 0.85);
  font-weight: 600;
}

.project-layout {
  display: grid;
  gap: 1.5rem;
}

@media (min-width: 800px) {
  .project-layout {
    grid-template-columns: 1.5fr 0.85fr;
    align-items: start;
  }
}

.project-body {
  font-size: 1.05rem;
  color: var(--muted);
  max-width: 40rem;
}

.project-media {
  margin-top: 2rem;
}

.project-media__grid {
  display: grid;
  gap: 0.75rem;
  grid-template-columns: 1fr 1fr;
}

.project-media__img {
  aspect-ratio: 4 / 3;
  border-radius: var(--radius);
  background: var(--clay-soft);
}

.project-media__item figcaption {
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: capitalize;
  color: var(--muted);
  margin-top: 0.3rem;
}

.side-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow);
  position: sticky;
  top: calc(var(--header-h) + 1rem);
}

.side-card h3 {
  margin-top: 0;
}

.side-card .btn {
  width: 100%;
}
</style>
