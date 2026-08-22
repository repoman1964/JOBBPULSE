<script setup lang="ts">
import type { ProjectCard } from '~/composables/usePublicApi'

const props = withDefaults(
  defineProps<{
    projects: ProjectCard[]
    emptyText?: string
    /** Max projects shown in the track (default 6). */
    limit?: number
  }>(),
  {
    limit: 6,
  },
)

const track = ref<HTMLElement | null>(null)
const canPrev = ref(false)
const canNext = ref(false)

const limited = computed(() => (props.projects || []).slice(0, props.limit))

function gapPx(el: HTMLElement): number {
  const style = getComputedStyle(el)
  const gap = parseFloat(style.columnGap || style.gap || '0')
  return Number.isFinite(gap) ? gap : 16
}

function cardStep(): number {
  const el = track.value
  if (!el) return 0
  const card = el.querySelector('.home-project-card') as HTMLElement | null
  if (!card) return Math.max(el.clientWidth * 0.33, 280)
  return card.getBoundingClientRect().width + gapPx(el)
}

function updateArrows() {
  const el = track.value
  if (!el) {
    canPrev.value = false
    canNext.value = false
    return
  }
  const max = el.scrollWidth - el.clientWidth
  canPrev.value = el.scrollLeft > 4
  canNext.value = el.scrollLeft < max - 4
}

function scrollByCard(dir: -1 | 1) {
  const el = track.value
  if (!el) return
  if (dir < 0 && !canPrev.value) return
  if (dir > 0 && !canNext.value) return
  const amount = cardStep() || Math.max(el.clientWidth * 0.33, 280)
  el.scrollBy({ left: dir * amount, behavior: 'smooth' })
}

onMounted(() => {
  updateArrows()
  track.value?.addEventListener('scroll', updateArrows, { passive: true })
  window.addEventListener('resize', updateArrows)
})

onBeforeUnmount(() => {
  track.value?.removeEventListener('scroll', updateArrows)
  window.removeEventListener('resize', updateArrows)
})

watch(
  () => limited.value.map((p) => p.id || p.slug).join('|'),
  async () => {
    await nextTick()
    updateArrows()
  },
)
</script>

<template>
  <div v-if="limited.length" class="project-carousel">
    <button
      type="button"
      class="project-carousel__arrow project-carousel__arrow--prev"
      :disabled="!canPrev"
      aria-label="Previous projects"
      @click="scrollByCard(-1)"
    >
      <span aria-hidden="true">‹</span>
    </button>

    <div ref="track" class="project-carousel__track" tabindex="0">
      <HomeProjectCard
        v-for="project in limited"
        :key="project.id || project.slug"
        :project="project"
      />
    </div>

    <button
      type="button"
      class="project-carousel__arrow project-carousel__arrow--next"
      :disabled="!canNext"
      aria-label="Next projects"
      @click="scrollByCard(1)"
    >
      <span aria-hidden="true">›</span>
    </button>
  </div>
  <div v-else class="empty">
    {{ emptyText || 'No projects to show yet.' }}
  </div>
</template>
