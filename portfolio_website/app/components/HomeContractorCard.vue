<script setup lang="ts">
import type { Contractor } from '~/composables/usePublicApi'
import { contractorCardImage } from '~/utils/contractorPlaceholders'
import { cityOnly } from '~/utils/locationLabel'

const props = defineProps<{
  contractor: Contractor
}>()

const imageSrc = computed(() => contractorCardImage(props.contractor))
</script>

<template>
  <NuxtLink
    :to="contractor.public_path || `/contractors/${contractor.slug}`"
    class="home-contractor-card"
  >
    <div class="home-contractor-card__media">
      <img
        :src="imageSrc"
        :alt="`${contractor.company_name} work`"
        class="home-contractor-card__photo"
        loading="lazy"
      />
    </div>
    <div class="home-contractor-card__body">
      <div class="home-contractor-card__row">
        <div class="home-contractor-card__identity">
          <ContractorAvatar :name="contractor.company_name" size="sm" />
          <h3 class="home-contractor-card__name">{{ contractor.company_name }}</h3>
        </div>
        <span v-if="contractor.featured" class="home-contractor-card__badge">Featured</span>
      </div>
      <p v-if="contractor.headline" class="home-contractor-card__headline">
        {{ contractor.headline }}
      </p>
      <p v-else-if="contractor.trade" class="home-contractor-card__headline">
        {{ contractor.trade }}
      </p>
      <div class="home-contractor-card__meta">
        <span v-if="cityOnly(contractor.primary_city)">
          {{ cityOnly(contractor.primary_city) }}
        </span>
        <span v-if="contractor.project_count != null">
          {{ contractor.project_count }} project{{ contractor.project_count === 1 ? '' : 's' }}
        </span>
      </div>
    </div>
  </NuxtLink>
</template>
