<script setup lang="ts">
export type ExpertiseTabService = {
  service_key: string
  display_name: string
}

export type ExpertiseFirstTab = {
  key: string
  label: string
}

const ESTIMATE_TAB = 'estimate'

const props = withDefaults(
  defineProps<{
    /** Active tab: firstTab.key | service_key | 'estimate' */
    modelValue: string
    services?: ExpertiseTabService[]
    showEstimate?: boolean
    ariaLabel?: string
    /** First tab (portfolio: All; profile: About us) */
    firstTab?: ExpertiseFirstTab
  }>(),
  {
    services: () => [],
    showEstimate: true,
    ariaLabel: 'Projects and estimate',
    firstTab: () => ({ key: 'all', label: 'All' }),
  },
)

const emit = defineEmits<{
  'update:modelValue': [value: string]
}>()

const firstKey = computed(() => props.firstTab?.key || 'all')
const firstLabel = computed(() => props.firstTab?.label || 'All')

function select(key: string) {
  emit('update:modelValue', key || firstKey.value)
}
</script>

<template>
  <div class="expertise-tabs" role="tablist" :aria-label="ariaLabel">
    <button
      type="button"
      role="tab"
      class="expertise-tabs__tab"
      :class="{ 'expertise-tabs__tab--active': modelValue === firstKey }"
      :aria-selected="modelValue === firstKey"
      @click="select(firstKey)"
    >
      {{ firstLabel }}
    </button>
    <button
      v-for="s in services"
      :key="s.service_key"
      type="button"
      role="tab"
      class="expertise-tabs__tab"
      :class="{ 'expertise-tabs__tab--active': modelValue === s.service_key }"
      :aria-selected="modelValue === s.service_key"
      @click="select(s.service_key)"
    >
      {{ s.display_name }}
    </button>
    <button
      v-if="showEstimate"
      type="button"
      role="tab"
      class="expertise-tabs__tab expertise-tabs__tab--estimate"
      :class="{ 'expertise-tabs__tab--active': modelValue === ESTIMATE_TAB }"
      :aria-selected="modelValue === ESTIMATE_TAB"
      @click="select(ESTIMATE_TAB)"
    >
      Request an estimate
    </button>
  </div>
</template>

<style scoped>
/* Areas-of-expertise style tabs (mockup: text row + orange underline) */
.expertise-tabs {
  --expertise-accent: #e85d04;
  display: flex;
  flex-wrap: wrap;
  align-items: stretch;
  justify-content: flex-start;
  gap: 0 1.35rem;
  margin: 0;
  padding: 0;
  border-bottom: 1px solid var(--border);
  width: 100%;
  box-sizing: border-box;
}

.expertise-tabs__tab {
  appearance: none;
  border: 0;
  background: transparent;
  color: #4b5563;
  padding: 0.55rem 0 0.65rem;
  margin: 0;
  font-size: 0.92rem;
  font-weight: 500;
  line-height: 1.2;
  cursor: pointer;
  border-bottom: 2px solid transparent;
  margin-bottom: -1px;
  white-space: nowrap;
}

.expertise-tabs__tab:hover {
  color: var(--text);
}

.expertise-tabs__tab--active {
  color: var(--expertise-accent);
  font-weight: 600;
  border-bottom-color: var(--expertise-accent);
}

.expertise-tabs__tab:focus-visible {
  outline: 2px solid var(--expertise-accent);
  outline-offset: 2px;
  border-radius: 2px;
}
</style>
