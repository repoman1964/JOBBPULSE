<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'

defineProps<{
  project: ProjectCard
}>()

function formatDate(value?: string | null) {
  if (!value) return ''
  try {
    return new Date(value).toLocaleDateString(undefined, {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    })
  } catch {
    return ''
  }
}
</script>

<template>
  <NuxtLink :to="project.public_path || `/projects/${project.slug}`" class="card project-card">
    <div class="project-card__media">
      <img
        v-if="project.primary_image_url"
        :src="project.primary_image_url"
        :alt="project.public_title"
        loading="lazy"
      />
      <div v-else class="project-card__placeholder">Project photo</div>
      <span v-if="project.has_before_after" class="badge badge--overlay">Before &amp; after</span>
    </div>
    <div class="project-card__body">
      <h3 class="project-card__title">{{ project.public_title }}</h3>
      <div class="project-card__meta">
        <span v-if="project.service_name || project.service_key">
          {{ project.service_name || project.service_key }}
        </span>
        <span v-if="project.city"> · {{ project.city }}{{ project.state ? `, ${project.state}` : '' }}</span>
      </div>
      <div v-if="project.contractor?.company_name" class="project-card__meta">
        {{ project.contractor.company_name }}
      </div>
      <p v-if="project.short_summary" class="project-card__summary">
        {{ project.short_summary }}
      </p>
      <div v-if="project.published_at" class="project-card__meta">
        {{ formatDate(project.published_at) }}
      </div>
    </div>
  </NuxtLink>
</template>
