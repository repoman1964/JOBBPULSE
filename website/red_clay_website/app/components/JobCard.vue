<script setup lang="ts">
import type { ProjectCard } from '~/composables/useJobPulse'
import { formatRelativeDate, projectImageStyle } from '~/utils/siteContent'

const props = defineProps<{
  project: ProjectCard
  compact?: boolean
}>()

const style = computed(() => {
  const url = props.project.primary_image_url
  // Skip known 1×1 seed placeholders; accept MinIO, CDN, and local /portfolio/* assets
  if (url && !url.includes('/demo/') && !url.endsWith('-0.png') && !url.endsWith('-1.png')) {
    return {
      backgroundImage: `url(${url})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
    }
  }
  return { background: projectImageStyle(props.project.public_title || props.project.slug) }
})
</script>

<template>
  <NuxtLink class="job-card" :class="{ 'job-card--compact': compact }" :to="`/work/${project.slug}`">
    <div class="job-card__media" :style="style">
      <span v-if="project.featured" class="job-card__featured">Featured</span>
    </div>
    <div class="job-card__body">
      <div class="job-card__meta">
        <span v-if="project.service_name" class="badge">{{ project.service_name }}</span>
        <span class="job-card__when">{{ formatRelativeDate(project.published_at) }}</span>
      </div>
      <h3 class="job-card__title">{{ project.public_title }}</h3>
      <p v-if="!compact && (project.short_summary || project.public_summary)" class="job-card__summary">
        {{ project.short_summary || project.public_summary }}
      </p>
      <p class="job-card__loc">{{ project.location_display || [project.city, project.state].filter(Boolean).join(', ') }}</p>
    </div>
  </NuxtLink>
</template>

<style scoped>
.job-card {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  text-decoration: none !important;
  color: inherit;
  box-shadow: var(--shadow);
  transition: transform 0.15s, box-shadow 0.15s;
  height: 100%;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
}

.job-card__media {
  aspect-ratio: 16 / 11;
  position: relative;
  background: var(--clay-soft);
}

.job-card--compact .job-card__media {
  aspect-ratio: 16 / 10;
}

.job-card__featured {
  position: absolute;
  top: 0.55rem;
  left: 0.55rem;
  background: rgba(28, 20, 16, 0.82);
  color: #fff;
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-pill);
}

.job-card__body {
  padding: 0.85rem 0.95rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  flex: 1;
}

.job-card__meta {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 0.35rem;
}

.job-card__when {
  font-size: 0.75rem;
  color: var(--muted);
  font-weight: 600;
}

.job-card__title {
  font-size: 1rem;
  margin: 0;
  color: var(--ink);
}

.job-card--compact .job-card__title {
  font-size: 0.92rem;
}

.job-card__summary {
  font-size: 0.88rem;
  color: var(--muted);
  margin: 0;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.job-card__loc {
  margin: auto 0 0;
  padding-top: 0.35rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--clay-dark);
}
</style>
