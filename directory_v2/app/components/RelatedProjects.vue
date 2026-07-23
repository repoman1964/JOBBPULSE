<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'

defineProps<{
  title: string
  projects?: ProjectCard[]
}>()
</script>

<template>
  <section v-if="projects?.length" class="section">
    <h2 class="section__title">{{ title }}</h2>
    <ProjectGallery :projects="projects" />
  </section>
</template>
