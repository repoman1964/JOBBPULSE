<script setup lang="ts">
import type { ProjectDetail } from '~/composables/usePublicApi'

const props = defineProps<{
  contractor: ProjectDetail['contractor']
  showAboutLink?: boolean
}>()

const portfolioTo = computed(() => {
  const c = props.contractor
  if (!c) return '#'
  if (c.portfolio_path) return c.portfolio_path
  if (c.slug) return `/contractors/${c.slug}/portfolio`
  return c.public_path || '#'
})

const profileTo = computed(() => {
  const c = props.contractor
  if (!c) return '#'
  if (c.public_path) return c.public_path
  if (c.about_path) return c.about_path
  if (c.slug) return `/contractors/${c.slug}`
  return '#'
})
</script>

<template>
  <div v-if="contractor" class="panel">
    <h2>Contractor</h2>
    <h3 style="margin: 0 0 0.35rem">{{ contractor.company_name || 'Local contractor' }}</h3>
    <p v-if="contractor.headline" class="muted" style="margin-top: 0">{{ contractor.headline }}</p>
    <p v-if="contractor.public_description">{{ contractor.public_description }}</p>
    <p v-if="contractor.trade" class="muted">Specialty: {{ contractor.trade }}</p>
    <div class="cta-actions">
      <NuxtLink class="btn btn-secondary" :to="portfolioTo">
        View portfolio
      </NuxtLink>
      <NuxtLink
        v-if="showAboutLink && profileTo !== '#'"
        class="btn btn-secondary"
        :to="profileTo"
      >
        About
      </NuxtLink>
      <a
        v-if="contractor.contact_phone"
        class="btn btn-primary"
        :href="`tel:${contractor.contact_phone}`"
      >
        Call
      </a>
    </div>
  </div>
</template>
