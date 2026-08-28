<script setup lang="ts">
import type { Job } from '~/types/domain'
import { PROCESSING_STEPS, processingStepState } from '~/utils/jobStatus'

const props = defineProps<{ job: Job }>()

const steps = computed(() =>
  PROCESSING_STEPS.map((step) => ({
    ...step,
    state: processingStepState(props.job.internalStatus, step.id),
  })),
)
</script>

<template>
  <section class="card processing" aria-live="polite">
    <div class="processing__head">
      <JpSpinner />
      <div>
        <h2 class="processing__title">Creating your content</h2>
        <p class="muted processing__sub">
          JobbPulse is working through your photos and voice note. This usually takes a short minute.
        </p>
      </div>
    </div>

    <ol class="processing__steps">
      <li
        v-for="step in steps"
        :key="step.id"
        class="processing__step"
        :class="`is-${step.state}`"
      >
        <span class="processing__mark">
          <JpSpinner v-if="step.state === 'active'" size="sm" />
          <span v-else-if="step.state === 'done'" class="processing__check" aria-hidden="true">✓</span>
        </span>
        <span>{{ step.label }}</span>
        <span v-if="step.state === 'active'" class="sr-only">In progress</span>
      </li>
    </ol>
  </section>
</template>

<style scoped>
.processing__head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 14px;
}

.processing__title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 800;
}

.processing__sub {
  margin: 4px 0 0;
  font-size: 0.88rem;
}

.processing__steps {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.processing__step {
  display: flex;
  align-items: center;
  gap: 10px;
  min-height: 28px;
  font-size: 0.92rem;
  color: var(--jp-text-dim);
}

.processing__step.is-active {
  color: var(--jp-text);
  font-weight: 650;
}

.processing__step.is-done {
  color: var(--jp-accent);
}

.processing__mark {
  width: 22px;
  height: 22px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.processing__check {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--jp-accent-dim);
  color: var(--jp-accent);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 0.75rem;
}
</style>
