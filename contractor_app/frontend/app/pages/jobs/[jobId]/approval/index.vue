<script setup lang="ts">
import type { ContentPackage, Job, MediaAsset } from '~/types/domain'
import { destinationLabel, statusLabel } from '~/utils/jobStatus'

const route = useRoute()
const api = useApi()
const { session } = useAuthSession()
const jobId = computed(() => String(route.params.jobId))
const companyName = computed(() => session.value?.company.name || 'Your company')

const job = ref<Job | null>(null)
const pkg = ref<ContentPackage | null>(null)
const media = ref<MediaAsset[]>([])
const loading = ref(true)
const error = ref('')
const publishing = ref(false)
const showFeatured = ref(false)
const showDescRev = ref(false)
const descInstruction = ref('')
const featuredBefore = ref('')
const featuredAfter = ref('')

const beforeUrl = computed(() => {
  const id = pkg.value?.featuredBeforeMediaId
  return media.value.find((m) => m.id === id)?.url
})
const afterUrl = computed(() => {
  const id = pkg.value?.featuredAfterMediaId
  return media.value.find((m) => m.id === id)?.url
})

async function load() {
  loading.value = true
  error.value = ''
  try {
    job.value = await api.getJob(jobId.value)
    pkg.value = await api.getPackage(jobId.value)
    media.value = await api.listMedia(jobId.value)
    featuredBefore.value = pkg.value?.featuredBeforeMediaId || ''
    featuredAfter.value = pkg.value?.featuredAfterMediaId || ''
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load package.'
  } finally {
    loading.value = false
  }
}

async function saveFeatured() {
  if (!featuredBefore.value || !featuredAfter.value) return
  pkg.value = await api.updateFeaturedMedia(jobId.value, featuredBefore.value, featuredAfter.value)
  showFeatured.value = false
}

async function requestDescChange() {
  if (!descInstruction.value.trim()) return
  pkg.value = await api.requestDescriptionRevision(jobId.value, descInstruction.value.trim())
  descInstruction.value = ''
  showDescRev.value = false
}

async function approve() {
  publishing.value = true
  error.value = ''
  try {
    const key = `publish-${jobId.value}-${Date.now()}`
    job.value = await api.approveAndPublish(jobId.value, key)
    setTimeout(async () => {
      job.value = await api.getJob(jobId.value)
    }, 1800)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Publish failed.'
  } finally {
    publishing.value = false
  }
}

const befores = computed(() => media.value.filter((m) => m.photoCategory === 'before'))
const afters = computed(() => media.value.filter((m) => m.photoCategory === 'after'))

onMounted(load)
</script>

<template>
  <div>
    <JpHeader show-back :back-to="`/jobs/${jobId}`" />
    <main class="app-main">
      <h1 class="page-title">Review &amp; Approve</h1>
      <template v-if="job">
        <p class="job-name">{{ job.name }}</p>
        <p class="muted">📍 {{ job.locationText }}</p>
        <StatusPill :label="statusLabel(job.publicStatus, job)" />
      </template>

      <div v-if="error" class="banner banner-error" role="alert" style="margin-top: 12px">{{ error }}</div>
      <p v-if="loading" class="muted">Loading package…</p>
      <p v-else-if="!pkg" class="banner" style="margin-top: 12px">
        JobbPulse is creating your content. We’ll let you know when it’s ready for approval.
      </p>

      <template v-else>
        <section class="card" style="margin-top: 16px">
          <h2 class="section-label">Featured transformation</h2>
          <div class="featured">
            <div class="featured-item">
              <img v-if="beforeUrl" :src="beforeUrl" alt="Featured before" />
              <span class="badge">BEFORE</span>
            </div>
            <div class="featured-item">
              <img v-if="afterUrl" :src="afterUrl" alt="Featured after" />
              <span class="badge">AFTER</span>
            </div>
          </div>
          <button type="button" class="link-lime" @click="showFeatured = !showFeatured">
            Change Featured Photos ›
          </button>
          <div v-if="showFeatured" class="stack" style="margin-top: 10px">
            <div class="field">
              <label>Before photo</label>
              <select v-model="featuredBefore">
                <option v-for="m in befores" :key="m.id" :value="m.id">{{ m.id }}</option>
              </select>
            </div>
            <div class="field">
              <label>After photo</label>
              <select v-model="featuredAfter">
                <option v-for="m in afters" :key="m.id" :value="m.id">{{ m.id }}</option>
              </select>
            </div>
            <button type="button" class="btn btn-primary" @click="saveFeatured">Save featured photos</button>
          </div>
        </section>

        <section class="card" style="margin-top: 12px">
          <h2 class="section-label">Project description</h2>
          <p class="desc">{{ pkg.projectDescription }}</p>
          <button type="button" class="btn btn-secondary" @click="showDescRev = !showDescRev">
            Request Text Change
          </button>
          <div v-if="showDescRev" class="stack" style="margin-top: 10px">
            <div class="field">
              <label for="descInst">What should change?</label>
              <textarea id="descInst" v-model="descInstruction" rows="3" placeholder="Describe the correction…" />
            </div>
            <button type="button" class="btn btn-primary" @click="requestDescChange">Submit change request</button>
          </div>
        </section>

        <section style="margin-top: 16px">
          <h2 class="section-label">Your JobbPulse content</h2>
          <div class="carousel" tabindex="0" aria-label="Generated content">
            <NuxtLink
              v-for="asset in pkg.assets"
              :key="asset.id"
              class="carousel-card"
              :to="`/jobs/${jobId}/approval/${asset.id}`"
            >
              <FacebookPostPreview
                v-if="asset.destinationType === 'facebook'"
                compact
                :company-name="companyName"
                :location="job?.locationText"
                :body="asset.body"
                :cover-url="(asset.preview.coverUrl as string) || null"
                :before-url="(asset.preview.beforeUrl as string) || null"
                :after-url="(asset.preview.afterUrl as string) || null"
              />
              <InstagramPostPreview
                v-else-if="asset.destinationType === 'instagram'"
                compact
                :company-name="companyName"
                :location="job?.locationText"
                :body="asset.body"
                :image-url="(asset.preview.coverUrl as string) || (asset.preview.afterUrl as string) || null"
              />
              <div v-else class="preview-frame card">
                <img
                  v-if="(asset.preview.coverUrl as string)"
                  :src="(asset.preview.coverUrl as string)"
                  :alt="`${destinationLabel(asset.destinationType)} preview`"
                />
                <p class="preview-body">{{ asset.body }}</p>
              </div>
              <div class="carousel-meta">
                <strong>{{ destinationLabel(asset.destinationType) }}</strong>
                <span class="link-lime">Tap to Review</span>
              </div>
            </NuxtLink>
          </div>
        </section>

        <button
          type="button"
          class="btn btn-primary"
          style="margin-top: 16px"
          :disabled="publishing || job?.publicStatus === 'publishing' || job?.publicStatus === 'published'"
          @click="approve"
        >
          <template v-if="job?.publicStatus === 'published'">Published</template>
          <template v-else-if="job?.publicStatus === 'publishing' || publishing">Publishing…</template>
          <template v-else>Approve &amp; Publish Everything</template>
        </button>
      </template>
    </main>
  </div>
</template>

<style scoped>
.job-name {
  margin: 4px 0;
  font-size: 1.15rem;
  font-weight: 700;
}

.featured {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin-bottom: 8px;
}

.featured-item {
  position: relative;
  border-radius: 12px;
  overflow: hidden;
  aspect-ratio: 1;
  background: #111;
}

.featured-item img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.badge {
  position: absolute;
  left: 50%;
  bottom: 8px;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.75);
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 0.7rem;
  font-weight: 800;
  letter-spacing: 0.04em;
}

.desc {
  margin: 0 0 12px;
  line-height: 1.45;
}

.carousel {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding-bottom: 8px;
  scroll-snap-type: x mandatory;
  -webkit-overflow-scrolling: touch;
}

.carousel-card {
  min-width: 82%;
  max-width: 82%;
  scroll-snap-align: start;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.preview-frame {
  background: #0f0f0f;
  border-radius: 12px;
  overflow: hidden;
  min-height: 180px;
}

.preview-frame img {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.preview-body {
  margin: 0;
  padding: 10px;
  font-size: 0.85rem;
  color: var(--jp-text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.carousel-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
</style>
