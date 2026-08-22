<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'

withDefaults(
  defineProps<{
    projects: ProjectCard[]
    emptyText?: string
    showContractor?: boolean
    showBeforeAfterBadge?: boolean
    compact?: boolean
  }>(),
  {
    showContractor: true,
    showBeforeAfterBadge: true,
    compact: false,
  },
)
</script>

<template>
  <div v-if="projects?.length" class="grid-projects">
    <ProjectCard
      v-for="project in projects"
      :key="project.id || project.slug"
      :project="project"
      :show-contractor="showContractor"
      :show-before-after-badge="showBeforeAfterBadge"
      :compact="compact"
    />
  </div>
  <div v-else class="empty">
    {{ emptyText || 'No projects to show yet.' }}
  </div>
</template>
