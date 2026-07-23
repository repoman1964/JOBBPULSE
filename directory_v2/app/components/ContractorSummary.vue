<script setup lang="ts">
import type { ProjectDetail } from '~/composables/usePublicApi'

defineProps<{
  contractor: ProjectDetail['contractor']
  showAboutLink?: boolean
}>()
</script>

<template>
  <div v-if="contractor" class="panel">
    <h2>Contractor</h2>
    <h3 style="margin: 0 0 0.35rem">{{ contractor.company_name || 'Local contractor' }}</h3>
    <p v-if="contractor.headline" class="muted" style="margin-top: 0">{{ contractor.headline }}</p>
    <p v-if="contractor.public_description">{{ contractor.public_description }}</p>
    <p v-if="contractor.trade" class="muted">Specialty: {{ contractor.trade }}</p>
    <div class="cta-actions">
      <NuxtLink
        v-if="contractor.public_path"
        class="btn btn-secondary"
        :to="contractor.public_path"
      >
        View portfolio
      </NuxtLink>
      <NuxtLink
        v-if="showAboutLink && contractor.about_path"
        class="btn btn-secondary"
        :to="contractor.about_path"
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
