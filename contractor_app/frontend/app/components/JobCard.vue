<script setup lang="ts">
import type { Job } from '~/types/domain'
import { contextualAction, statusLabel } from '~/utils/jobStatus'

const props = defineProps<{ job: Job }>()

const action = computed(() => contextualAction(props.job))
const label = computed(() => statusLabel(props.job.publicStatus, props.job))
</script>

<template>
  <article class="job-card card card-tight">
    <div class="job-card__cover">
      <img
        v-if="job.coverUrl"
        :src="job.coverUrl"
        :alt="`${job.name} cover photo`"
        loading="lazy"
      />
      <div v-else class="job-card__cover-empty" aria-hidden="true" />
      <div class="job-card__pill">
        <StatusPill :label="label" />
      </div>
    </div>

    <div class="job-card__body">
      <h2 class="job-card__title">
        <NuxtLink :to="`/jobs/${job.id}`">{{ job.name }}</NuxtLink>
      </h2>
      <p class="job-card__loc muted">
        <span aria-hidden="true">📍</span>
        {{ job.locationText || `${job.city}, ${job.region}` }}
      </p>

      <div class="job-card__counts" aria-label="Photo counts">
        <div>
          <span class="dim">BEFORE</span>
          <strong>{{ job.counts.before }}</strong>
        </div>
        <div class="divider" aria-hidden="true" />
        <div>
          <span class="dim">PROGRESS</span>
          <strong>{{ job.counts.progress }}</strong>
        </div>
        <div class="divider" aria-hidden="true" />
        <div>
          <span class="dim">AFTER</span>
          <strong>{{ job.counts.after }}</strong>
        </div>
      </div>

      <NuxtLink class="btn btn-primary" :to="action.to">
        <span v-if="action.icon === 'camera'" aria-hidden="true">📷</span>
        <span v-else-if="action.icon === 'eye'" aria-hidden="true">👁</span>
        {{ action.label }}
      </NuxtLink>
    </div>
  </article>
</template>

<style scoped>
.job-card {
  padding: 0;
  overflow: hidden;
}

.job-card__cover {
  position: relative;
  aspect-ratio: 16 / 10;
  background: #111;
}

.job-card__cover img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.job-card__cover-empty {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #1a1a1a, #2a2a2a);
}

.job-card__pill {
  position: absolute;
  top: 12px;
  left: 12px;
}

.job-card__body {
  padding: 14px 14px 16px;
}

.job-card__title {
  margin: 0 0 4px;
  font-size: 1.15rem;
  font-weight: 800;
}

.job-card__title a {
  color: inherit;
}

.job-card__loc {
  margin: 0 0 14px;
  font-size: 0.9rem;
}

.job-card__counts {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  align-items: center;
  text-align: center;
  margin-bottom: 14px;
  gap: 4px;
}

.job-card__counts span {
  display: block;
  font-size: 0.65rem;
  font-weight: 700;
  letter-spacing: 0.06em;
  margin-bottom: 2px;
}

.job-card__counts strong {
  font-size: 1.35rem;
  font-weight: 800;
}

.divider {
  width: 1px;
  height: 28px;
  background: var(--jp-card-border);
}
</style>
