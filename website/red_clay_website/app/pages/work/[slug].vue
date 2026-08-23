<script setup lang="ts">
import { isDummySlug } from '~/utils/demoProjects'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
const demo = useDemoProjects()
const notFound = ref(false)

const title = ref('Project')
const summary = ref('')
const serviceType = ref('')
const city = ref('')
const beforeUrl = ref<string | null>(null)
const afterUrl = ref<string | null>(null)
const socialPosts = ref<{ destination: string; title: string; body: string; imageUrl?: string | null }[]>([])

await (async () => {
  const dummy = demo.dummyDetail(slug.value)
  if (!isDummySlug(slug.value)) {
    const live = await demo.fetchLiveDetail(slug.value)
    if (live) {
      title.value = live.publicTitle
      summary.value = live.publicSummary
      serviceType.value = live.serviceType
      city.value = live.city
      const before = live.media?.find((m) => m.stageLabel === 'before')
      const after = live.media?.find((m) => m.stageLabel === 'after')
      beforeUrl.value = before?.url || null
      afterUrl.value = after?.url || live.primaryImageUrl || null
      socialPosts.value = live.socialPosts || []
      return
    }
  }
  if (dummy) {
    title.value = dummy.publicTitle
    summary.value = dummy.publicSummary
    serviceType.value = dummy.serviceType
    city.value = dummy.city
    beforeUrl.value = dummy.beforeUrl
    afterUrl.value = dummy.afterUrl
    socialPosts.value = dummy.socialPosts
    return
  }
  notFound.value = true
})()

useSeoMeta({
  title: () => `${title.value} | Red Clay`,
  description: () => summary.value || 'Painted project in metro Atlanta.',
})
</script>

<template>
  <div>
    <section v-if="notFound" class="section">
      <div class="container">
        <h1>Project not found</h1>
        <p>That job is not on the site.</p>
        <NuxtLink class="btn btn--primary" to="/work">Back to work</NuxtLink>
      </div>
    </section>
    <template v-else>
      <section class="page-hero">
        <div class="container">
          <p class="section__eyebrow">{{ city }} · {{ serviceType }}</p>
          <h1 class="page-hero__title">{{ title }}</h1>
          <p class="section__lead">{{ summary }}</p>
        </div>
      </section>
      <section class="section">
        <div class="container">
          <BeforeAfter
            :before-url="beforeUrl"
            :after-url="afterUrl"
            :before-alt="`Before — ${title}`"
            :after-alt="`After — ${title}`"
          />
        </div>
      </section>
      <section class="section" style="background: var(--card)">
        <div class="container silo-layout">
          <div>
            <p class="section__eyebrow">The job</p>
            <h2>{{ title }}</h2>
            <p>{{ summary }}</p>
          </div>
          <aside class="silo-aside__card">
            <h2>Ready for a quote?</h2>
            <p>Walk the house. Get a written number.</p>
            <NuxtLink class="btn btn--primary" to="/book">Book an estimate</NuxtLink>
          </aside>
        </div>
      </section>
      <section class="section">
        <div class="container">
          <p class="section__eyebrow">Shared from this job</p>
          <h2>Facebook, Instagram, and Google Business</h2>
          <SocialCards :posts="socialPosts" />
        </div>
      </section>
    </template>
  </div>
</template>
