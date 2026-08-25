<script setup lang="ts">
import { COMPANY } from '~/utils/siteContent'

export type SocialCard = {
  destination: string
  title: string
  body: string
  imageUrl?: string | null
  groupName?: string | null
}

const props = withDefaults(
  defineProps<{
    posts: SocialCard[]
    companyName?: string
    location?: string
    beforeUrl?: string | null
    afterUrl?: string | null
  }>(),
  {
    companyName: COMPANY.name,
  },
)

const labels: Record<string, string> = {
  facebook: 'Facebook',
  facebook_group: 'Facebook Group',
  instagram: 'Instagram',
  google_business: 'Google Business',
}

const ordered = computed(() => {
  const rank = ['facebook', 'facebook_group', 'instagram', 'google_business']
  return [...props.posts].sort((a, b) => {
    const ia = rank.indexOf(a.destination)
    const ib = rank.indexOf(b.destination)
    return (ia === -1 ? rank.length : ia) - (ib === -1 ? rank.length : ib)
  })
})

const cover = (post: SocialCard) => post.imageUrl || props.afterUrl || props.beforeUrl || ''

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
  const card = el.querySelector<HTMLElement>('.social-slot')
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
  () => props.posts.length,
  async () => {
    await nextTick()
    updateNav()
  },
)
</script>

<template>
  <div v-if="ordered.length" class="carousel-wrap">
    <button
      type="button"
      class="carousel__nav carousel__nav--prev"
      aria-label="Previous social post"
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
      aria-label="Generated social posts"
      @keydown="onKeydown"
    >
    <div v-for="post in ordered" :key="post.destination" class="social-slot" role="listitem">
      <p class="section__eyebrow">{{ labels[post.destination] || post.destination }}</p>

      <FacebookPostPreview
        v-if="post.destination === 'facebook'"
        compact
        :company-name="companyName"
        :location="location"
        :body="post.body"
        :cover-url="cover(post)"
        :before-url="beforeUrl"
        :after-url="afterUrl"
      />
      <FacebookGroupPostPreview
        v-else-if="post.destination === 'facebook_group'"
        compact
        :company-name="companyName"
        :group-name="post.groupName || 'Neighborhood group'"
        :location="location"
        :body="post.body"
        :cover-url="cover(post)"
        :before-url="beforeUrl"
        :after-url="afterUrl"
      />
      <InstagramPostPreview
        v-else-if="post.destination === 'instagram'"
        compact
        :company-name="companyName"
        :location="location"
        :body="post.body"
        :image-url="cover(post)"
      />
      <GoogleBusinessPostPreview
        v-else-if="post.destination === 'google_business'"
        compact
        :company-name="companyName"
        :location="location"
        :body="post.body"
        :image-url="cover(post)"
      />
    </div>
    </div>
    <button
      type="button"
      class="carousel__nav carousel__nav--next"
      aria-label="Next social post"
      :disabled="!canNext"
      @click="scrollByDir(1)"
    >
      ›
    </button>
  </div>
</template>
