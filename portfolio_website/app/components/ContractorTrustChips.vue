<script setup lang="ts">
import type { DemoTrustChip } from '~/utils/contractorDemo'

defineProps<{
  chips: DemoTrustChip[]
}>()
</script>

<template>
  <ul v-if="chips?.length" class="trust-chips" aria-label="Contractor highlights">
    <li v-for="(chip, i) in chips" :key="i" class="trust-chips__item">
      {{ chip.label }}
    </li>
  </ul>
</template>

<style scoped>
.trust-chips {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.65rem;
  list-style: none;
  /* ~75% viewport, centered on the page */
  width: min(75vw, 100%);
  margin: 1rem auto 0;
  padding: 0;
  box-sizing: border-box;
}

.trust-chips__item {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  min-width: 0;
  padding: 0.45rem 0.65rem;
  border-radius: var(--radius-pill);
  background: #eef2f7;
  color: var(--text);
  font-size: 0.82rem;
  font-weight: 600;
  border: 1px solid #e2e8f0;
  line-height: 1.25;
}

@media (max-width: 720px) {
  .trust-chips {
    grid-template-columns: repeat(2, minmax(0, 1fr));
    width: 100%;
  }
}

@media (max-width: 420px) {
  .trust-chips {
    grid-template-columns: 1fr;
  }
}
</style>
