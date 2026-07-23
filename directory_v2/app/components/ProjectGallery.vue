<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'

defineProps<{
  projects: ProjectCard[]
  emptyText?: string
}>()
</script>

<template>
  <div v-if="projects?.length" class="grid-projects">
    <ProjectCard v-for="project in projects" :key="project.id || project.slug" :project="project" />
  </div>
  <div v-else class="empty">
    {{ emptyText || 'No projects to show yet.' }}
  </div>
</template>
