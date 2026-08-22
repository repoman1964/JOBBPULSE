<script setup lang="ts">
const route = useRoute()
const api = usePublicApi()
const nuxtApp = useNuxtApp()

/** Always derive from the URL so client navigations re-sync filters. */
const q = computed(() => (typeof route.query.q === 'string' ? route.query.q : ''))
const service = computed(() =>
  typeof route.query.service_key === 'string' ? route.query.service_key : '',
)

/** Local form fields (editable); seeded from the route. */
const qInput = ref(q.value)
const serviceInput = ref(service.value)

watch(
  () => [q.value, service.value] as const,
  ([nextQ, nextService]) => {
    qInput.value = nextQ
    serviceInput.value = nextService
  },
)

const { data, pending, error, refresh } = await useAsyncData(
  () => `contractors-index-${q.value}-${service.value}`,
  () =>
    api.listContractors({
      q: q.value || undefined,
      service_key: service.value || undefined,
      limit: 40,
    }),
  {
    watch: [q, service],
    // Use SSR payload only on first hydration. On client-side navigations back
    // to this page, always re-fetch so we never show a cleared/stale cache.
    getCachedData(key) {
      if (nuxtApp.isHydrating) {
        return nuxtApp.payload.data[key]
      }
      return undefined
    },
  },
)

const { data: services } = await useAsyncData('contractors-services-filter', () =>
  api.listServices(),
)

useSeoMeta({
  title: 'Contractors | JobPulse',
  description: 'Contractors with documented completed projects on JobPulse.',
})

function applyFilters() {
  return navigateTo({
    path: '/contractors',
    query: {
      ...(qInput.value ? { q: qInput.value } : {}),
      ...(serviceInput.value ? { service_key: serviceInput.value } : {}),
    },
  })
}
</script>

<template>
  <div class="container contractors-page">
    <form class="contractors-toolbar" @submit.prevent="applyFilters">
      <select
        v-model="serviceInput"
        class="contractors-toolbar__services"
        aria-label="Filter by services"
        @change="applyFilters"
      >
        <option value="">Show all services</option>
        <option v-for="s in services?.items || []" :key="s.slug" :value="s.service_key">
          {{ s.name }}
        </option>
      </select>
      <label class="contractors-toolbar__search">
        <input
          v-model="qInput"
          type="search"
          class="contractors-toolbar__search-input"
          placeholder="Find a contractor"
          aria-label="Find a contractor"
        />
        <!-- Icon is a flex sibling inside the bordered shell (right edge, not outside) -->
        <span class="contractors-toolbar__search-icon" aria-hidden="true">
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width="30"
            height="30"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            stroke-width="1.75"
            stroke-linecap="round"
            stroke-linejoin="round"
            style="width: 30px; height: 30px; flex-shrink: 0"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="m20 20-3.5-3.5" />
          </svg>
        </span>
      </label>
    </form>

    <p v-if="pending" class="muted">Loading…</p>

    <p v-else-if="error" class="empty">
      Could not load contractors.
      <button type="button" class="btn btn-secondary" style="margin-left: 0.5rem" @click="refresh()">
        Retry
      </button>
    </p>

    <div v-else-if="data?.items?.length" class="grid-projects">
      <HomeContractorCard
        v-for="c in data.items"
        :key="c.slug"
        :contractor="c"
      />
    </div>

    <div v-else class="empty">No published contractors match these filters.</div>
  </div>
</template>

<style scoped>
.contractors-page {
  padding-top: 1rem;
  padding-bottom: 2rem;
}

/* Services far left + search far right — flush with card grid edges */
.contractors-toolbar {
  display: flex;
  align-items: center;
  margin: 0 0 1.25rem;
  width: 100%;
}

.contractors-toolbar__services {
  flex: 0 0 auto;
  margin-right: auto;
  margin-left: 0;
  border: 1px solid var(--border);
  border-radius: 8px;
  /* Room for 30px chevron + right inset */
  padding: 0.5rem 3.25rem 0.5rem 0.85rem;
  background-color: var(--surface);
  color: var(--text);
  font-size: 14px;
  min-width: 12rem;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='30' height='30' viewBox='0 0 24 24' fill='none' stroke='%236b7280' stroke-width='2.25' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.65rem center;
  background-size: 30px 30px;
  cursor: pointer;
}

.contractors-toolbar__services::-ms-expand {
  display: none;
}

/* Visual search box: text + magnifying glass share one bordered shell */
.contractors-toolbar__search {
  display: flex;
  flex-direction: row;
  align-items: center;
  flex: 0 0 230px;
  width: 230px;
  max-width: 100%;
  margin-left: auto;
  box-sizing: border-box;
  border: 1px solid var(--border);
  border-radius: 8px;
  background: var(--surface);
  padding: 0.4rem 0.5rem 0.4rem 0.85rem;
  gap: 0.4rem;
  min-height: 3.25rem;
  cursor: text;
}

/* Desktop: fixed 50px height for services dropdown + search */
@media (min-width: 768px) {
  .contractors-toolbar__services {
    height: 50px;
    min-height: 50px;
    max-height: 50px;
    box-sizing: border-box;
    padding: 0 3.25rem 0 0.85rem;
    line-height: normal;
  }

  .contractors-toolbar__search {
    height: 50px;
    min-height: 50px;
    max-height: 50px;
    padding-top: 0;
    padding-bottom: 0;
  }

  .contractors-toolbar__search-input {
    padding-top: 0;
    padding-bottom: 0;
    line-height: 1;
  }
}

.contractors-toolbar__search-input {
  flex: 1 1 auto;
  min-width: 0;
  width: auto;
  border: 0;
  outline: none;
  box-shadow: none;
  background: transparent;
  color: var(--text);
  padding: 0.35rem 0;
  font: inherit;
  font-size: 14px;
  line-height: 1.3;
}

.contractors-toolbar__search-input::-webkit-search-decoration,
.contractors-toolbar__search-input::-webkit-search-cancel-button,
.contractors-toolbar__search-input::-webkit-search-results-button,
.contractors-toolbar__search-input::-webkit-search-results-decoration {
  -webkit-appearance: none;
  appearance: none;
  display: none;
}

/* Magnifying glass: INSIDE the shell, floated to the far right */
.contractors-toolbar__search-icon {
  flex: 0 0 30px;
  width: 30px;
  height: 30px;
  margin-left: auto;
  margin-right: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: var(--muted);
  pointer-events: none;
  line-height: 0;
}

.contractors-toolbar__search-icon svg {
  width: 30px !important;
  height: 30px !important;
  max-width: none;
  display: block;
}
</style>
