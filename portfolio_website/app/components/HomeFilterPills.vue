<script setup lang="ts">
type FilterOption = { value: string; label: string; to: string }

const props = defineProps<{
  services: FilterOption[]
  locations: FilterOption[]
  contractors: FilterOption[]
}>()

const openKey = ref<'service' | 'location' | 'contractor' | null>(null)
const root = ref<HTMLElement | null>(null)

const menus = computed(() => [
  { key: 'service' as const, label: 'Service', options: props.services },
  { key: 'location' as const, label: 'Location', options: props.locations },
  { key: 'contractor' as const, label: 'Contractor', options: props.contractors },
])

function toggle(key: typeof openKey.value) {
  openKey.value = openKey.value === key ? null : key
}

function choose(to: string) {
  openKey.value = null
  navigateTo(to)
}

function onDocClick(e: MouseEvent) {
  if (!root.value) return
  if (!root.value.contains(e.target as Node)) openKey.value = null
}

function onKey(e: KeyboardEvent) {
  if (e.key === 'Escape') openKey.value = null
}

onMounted(() => {
  document.addEventListener('click', onDocClick)
  document.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  document.removeEventListener('click', onDocClick)
  document.removeEventListener('keydown', onKey)
})
</script>

<template>
  <div ref="root" class="home-filters" role="group" aria-label="Filter projects">
    <div v-for="menu in menus" :key="menu.key" class="home-filters__item">
      <button
        type="button"
        class="home-filters__pill"
        :class="{ 'is-open': openKey === menu.key }"
        :aria-expanded="openKey === menu.key"
        :aria-controls="`filter-menu-${menu.key}`"
        @click="toggle(menu.key)"
      >
        <span>{{ menu.label }}</span>
        <span class="home-filters__chevron" aria-hidden="true">{{ openKey === menu.key ? '▴' : '▾' }}</span>
      </button>
      <div
        v-show="openKey === menu.key"
        :id="`filter-menu-${menu.key}`"
        class="home-filters__menu"
        role="listbox"
        :aria-label="menu.label"
      >
        <p v-if="!menu.options.length" class="home-filters__empty muted">No options yet</p>
        <button
          v-for="opt in menu.options"
          :key="opt.value"
          type="button"
          class="home-filters__option"
          role="option"
          @click="choose(opt.to)"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>
  </div>
</template>
