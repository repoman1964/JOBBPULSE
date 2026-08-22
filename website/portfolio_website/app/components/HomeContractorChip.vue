<script setup lang="ts">
import type { Contractor } from '~/composables/usePublicApi'

defineProps<{
  contractor: Contractor
}>()
</script>

<template>
  <NuxtLink
    :to="contractor.public_path || `/contractors/${contractor.slug}`"
    class="home-contractor-chip"
  >
    <ContractorAvatar :name="contractor.company_name" size="md" />
    <span class="home-contractor-chip__name">{{ contractor.company_name }}</span>
  </NuxtLink>
</template>
