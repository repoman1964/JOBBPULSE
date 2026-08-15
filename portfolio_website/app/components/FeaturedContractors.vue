<script setup lang="ts">
import type { Contractor } from '~/composables/usePublicApi'

defineProps<{
  contractors: Contractor[]
}>()
</script>

<template>
  <div v-if="contractors?.length" class="grid-projects">
    <NuxtLink
      v-for="c in contractors"
      :key="c.slug"
      :to="c.public_path || `/contractors/${c.slug}`"
      class="card contractor-card"
    >
      <h3>{{ c.company_name }}</h3>
      <p class="muted" style="margin: 0">
        {{ c.project_count ?? c.recent_projects?.length ?? 0 }} documented projects
      </p>
      <p v-if="c.headline" class="muted" style="margin: 0.35rem 0 0">{{ c.headline }}</p>
    </NuxtLink>
  </div>
</template>
