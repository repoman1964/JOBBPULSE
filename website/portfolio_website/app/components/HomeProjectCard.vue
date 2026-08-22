<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'
import { projectCardImage } from '~/utils/projectPlaceholders'

const props = withDefaults(
  defineProps<{
    project: ProjectCard
    /** Hide name/avatar when the page is already for this contractor. */
    showContractor?: boolean
  }>(),
  { showContractor: true },
)

const imageSrc = computed(() => projectCardImage(props.project))
</script>

<template>
  <NuxtLink
    :to="project.public_path || `/projects/${project.slug}`"
    class="home-project-card"
  >
    <div class="home-project-card__media">
      <img
        :src="imageSrc"
        :alt="project.public_title"
        loading="lazy"
      />
    </div>
    <div class="home-project-card__body">
      <h3 class="home-project-card__title">{{ project.public_title }}</h3>
      <p v-if="project.city" class="home-project-card__city">{{ project.city }}</p>
      <div
        v-if="showContractor && project.contractor?.company_name"
        class="home-project-card__contractor"
      >
        <ContractorAvatar :name="project.contractor.company_name" size="sm" />
        <span>{{ project.contractor.company_name }}</span>
      </div>
    </div>
  </NuxtLink>
</template>
