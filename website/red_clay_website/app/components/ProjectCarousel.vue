<script setup lang="ts">
import type { CarouselJob } from '~/utils/demoProjects'

const props = defineProps<{ jobs: CarouselJob[] }>()

const track = ref<HTMLElement | null>(null)
const canPrev = ref(false)
const canNext = ref(false)

function updateNav() {
  const el = track.value
  if (!el) {
    canPrev.value = false
    canNext.value = false
    return
  }
  const max = el.scrollWidth - el.clientWidth
  canPrev.value = el.scrollLeft > 8
  canNext.value = el.scrollLeft < max - 8
}

function scrollByDir(dir: -1 | 1) {
  const el = track.value
  if (!el) return
  const card = el.querySelector<HTMLElement>('.project-card')
  const styles = getComputedStyle(el)
  const gap = Number.parseFloat(styles.columnGap || styles.gap) || 20
  const amount = (card?.offsetWidth || 320) + gap
  el.scrollBy({ left: dir * amount, behavior: 'smooth' })
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'ArrowRight') {
    event.preventDefault()
    scrollByDir(1)
  } else if (event.key === 'ArrowLeft') {
    event.preventDefault()
    scrollByDir(-1)
  }
}

onMounted(() => {
  updateNav()
  track.value?.addEventListener('scroll', updateNav, { passive: true })
  window.addEventListener('resize', updateNav)
})

onBeforeUnmount(() => {
  track.value?.removeEventListener('scroll', updateNav)
  window.removeEventListener('resize', updateNav)
})

watch(
  () => props.jobs[0]?.slug,
  async () => {
    await nextTick()
    if (track.value) track.value.scrollLeft = 0
    updateNav()
  },
)
</script>

<template>
  <div class="carousel-wrap">
    <button
      type="button"
      class="carousel__nav carousel__nav--prev"
      aria-label="Previous projects"
      :disabled="!canPrev"
      @click="scrollByDir(-1)"
    >
      ‹
    </button>
    <div
      ref="track"
      class="carousel"
      role="list"
      tabindex="0"
      aria-label="Recent projects"
      @keydown="onKeydown"
    >
      <NuxtLink
        v-for="job in jobs"
        :key="job.slug"
        class="project-card"
        :to="`/work/${job.slug}`"
        role="listitem"
      >
        <img
          :src="job.primaryImageUrl || '/images/exterior.jpg'"
          :alt="job.publicTitle"
          width="800"
          height="450"
        />
        <div class="project-card__body">
          <p class="section__eyebrow">{{ job.city }} · {{ job.serviceType }}</p>
          <h3>{{ job.publicTitle }}</h3>
          <p>{{ job.publicSummary }}</p>
        </div>
      </NuxtLink>
    </div>
    <button
      type="button"
      class="carousel__nav carousel__nav--next"
      aria-label="Next projects"
      :disabled="!canNext"
      @click="scrollByDir(1)"
    >
      ›
    </button>
  </div>
</template>
