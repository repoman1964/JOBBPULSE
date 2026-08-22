<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'
import { cityOnly } from '~/utils/locationLabel'

const props = withDefaults(
  defineProps<{
    project: ProjectCard
    /** Hide contractor name when already on that contractor’s page. */
    showContractor?: boolean
    /** Hide “Before & after” media badge. */
    showBeforeAfterBadge?: boolean
    /**
     * Portfolio-style card: title + “Service - Location” meta only
     * (no summary/date). Titles come from the API as-is.
     */
    compact?: boolean
  }>(),
  {
    showContractor: true,
    showBeforeAfterBadge: true,
    compact: false,
  },
)

const serviceLabel = computed(
  () => props.project.service_name || props.project.service_key || '',
)

const locationLabel = computed(() =>
  cityOnly(props.project.city, props.project.location_display),
)

const compactMeta = computed(() => {
  const parts = [serviceLabel.value, locationLabel.value].filter(Boolean)
  return parts.join(' - ')
})

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
      <span
        v-if="showBeforeAfterBadge && project.has_before_after"
        class="badge badge--overlay"
      >
        Before &amp; after
      </span>
    </div>
    <div class="project-card__body">
      <h3 class="project-card__title">{{ project.public_title }}</h3>
      <div v-if="compact && compactMeta" class="project-card__meta">
        {{ compactMeta }}
      </div>
      <div v-else-if="!compact" class="project-card__meta">
        <span v-if="serviceLabel">{{ serviceLabel }}</span>
        <span v-if="locationLabel"> · {{ locationLabel }}</span>
      </div>
      <div v-if="showContractor && project.contractor?.company_name" class="project-card__meta">
        {{ project.contractor.company_name }}
      </div>
      <p v-if="!compact && project.short_summary" class="project-card__summary">
        {{ project.short_summary }}
      </p>
      <div v-if="!compact && project.published_at" class="project-card__meta">
        {{ formatDate(project.published_at) }}
      </div>
    </div>
  </NuxtLink>
</template>
