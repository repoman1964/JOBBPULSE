<script setup lang="ts">
import type { GeneratedAsset, Job } from '~/types/domain'
import { destinationLabel, statusLabel } from '~/utils/jobStatus'

const route = useRoute()
const api = useApi()
const jobId = computed(() => String(route.params.jobId))
const assetId = computed(() => String(route.params.assetId))

const job = ref<Job | null>(null)
const asset = ref<GeneratedAsset | null>(null)
const loading = ref(true)
const error = ref('')
const mode = ref<'view' | 'wording' | 'compare'>('view')
const instruction = ref('')
const pendingVersionId = ref<string | null>(null)

async function load() {
  loading.value = true
  error.value = ''
  try {
    job.value = await api.getJob(jobId.value)
    asset.value = await api.getGeneratedAsset(assetId.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load content.'
  } finally {
    loading.value = false
  }
}

async function requestWording() {
  if (!instruction.value.trim() || !asset.value) return
  asset.value = await api.requestAssetRevision(asset.value.id, {
    changeType: 'wording',
    instructionText: instruction.value.trim(),
  })
  const latest = asset.value.versions[asset.value.versions.length - 1]
  pendingVersionId.value = latest?.id || null
  mode.value = 'compare'
  instruction.value = ''
}

async function useNew() {
  if (!asset.value || !pendingVersionId.value) return
  asset.value = await api.selectAssetVersion(asset.value.id, pendingVersionId.value)
  pendingVersionId.value = null
  mode.value = 'view'
  await navigateTo(`/jobs/${jobId.value}/approval`)
}

async function keepOriginal() {
  pendingVersionId.value = null
  mode.value = 'view'
  await navigateTo(`/jobs/${jobId.value}/approval`)
}

async function keepThis() {
  await navigateTo(`/jobs/${jobId.value}/approval`)
}

const activeVersion = computed(() =>
  asset.value?.versions.find((v) => v.id === asset.value?.activeVersionId),
)
const pendingVersion = computed(() =>
  asset.value?.versions.find((v) => v.id === pendingVersionId.value),
)

const previewComponent = computed(() => {
  const t = asset.value?.destinationType
  if (t === 'instagram') return 'instagram'
  if (t === 'facebook') return 'facebook'
  return 'website'
})

onMounted(load)
</script>

<template>
  <div>
    <JpHeader show-back :back-to="`/jobs/${jobId}/approval`" />
    <main class="app-main">
      <p v-if="loading" class="muted">Loading…</p>
      <div v-else-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <template v-else-if="asset && job">
        <h1 class="page-title" style="font-size: 1.4rem">
          {{ destinationLabel(asset.destinationType) }}
        </h1>
        <p class="muted" style="margin: 0 0 8px">{{ job.name }}</p>
        <StatusPill :label="statusLabel(job.publicStatus, job)" />

        <div class="preview-shell card" style="margin-top: 16px">
          <div v-if="previewComponent === 'instagram'" class="ig">
            <div class="ig-top">
              <strong>jobbpulse_construction</strong>
              <span class="muted">{{ job.city }}, {{ job.region }}</span>
            </div>
            <img
              v-if="(asset.preview.coverUrl as string)"
              :src="(asset.preview.coverUrl as string)"
              alt="Instagram preview"
            />
            <p class="body">{{ activeVersion?.body || asset.body }}</p>
          </div>
          <div v-else-if="previewComponent === 'facebook'" class="fb">
            <div class="fb-top">
              <strong>JobbPulse Construction</strong>
              <span class="muted">Just now · 🌎</span>
            </div>
            <p class="body">{{ activeVersion?.body || asset.body }}</p>
            <div class="fb-images">
              <img v-if="(asset.preview.beforeUrl as string)" :src="(asset.preview.beforeUrl as string)" alt="Before" />
              <img v-if="(asset.preview.afterUrl as string)" :src="(asset.preview.afterUrl as string)" alt="After" />
            </div>
          </div>
          <div v-else class="web">
            <p class="section-label">Recent project</p>
            <h2>{{ job.name }}</h2>
            <p class="muted">📍 {{ job.locationText }}</p>
            <div class="web-imgs">
              <img v-if="(asset.preview.beforeUrl as string)" :src="(asset.preview.beforeUrl as string)" alt="Before" />
              <img v-if="(asset.preview.afterUrl as string)" :src="(asset.preview.afterUrl as string)" alt="After" />
            </div>
            <p class="body">{{ activeVersion?.body || asset.body }}</p>
          </div>
        </div>

        <div v-if="mode === 'view'" class="stack" style="margin-top: 14px">
          <button type="button" class="btn btn-secondary" @click="mode = 'wording'">Change Wording</button>
          <button type="button" class="btn btn-secondary" @click="mode = 'wording'">Describe Another Change</button>
          <button type="button" class="btn btn-primary" @click="keepThis">Keep This Version</button>
        </div>

        <div v-else-if="mode === 'wording'" class="card stack" style="margin-top: 14px">
          <div class="field">
            <label for="inst">What should change?</label>
            <textarea id="inst" v-model="instruction" rows="3" placeholder="Explain the correction…" />
          </div>
          <button type="button" class="btn btn-primary" @click="requestWording">Submit revision</button>
          <button type="button" class="btn btn-secondary" @click="mode = 'view'">Cancel</button>
        </div>

        <div v-else-if="mode === 'compare'" class="stack" style="margin-top: 14px">
          <div class="card">
            <h3 class="section-label">New version</h3>
            <p>{{ pendingVersion?.body }}</p>
          </div>
          <div class="card">
            <h3 class="section-label">Original</h3>
            <p>{{ activeVersion?.body }}</p>
          </div>
          <button type="button" class="btn btn-primary" @click="useNew">Use New Version</button>
          <button type="button" class="btn btn-secondary" @click="keepOriginal">Keep Original</button>
        </div>
      </template>
    </main>
  </div>
</template>

<style scoped>
.preview-shell {
  padding: 0;
  overflow: hidden;
}

.ig-top,
.fb-top {
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.ig img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
}

.body {
  padding: 12px;
  margin: 0;
  line-height: 1.45;
  font-size: 0.95rem;
}

.fb-images,
.web-imgs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 4px;
  padding: 0 12px 12px;
}

.fb-images img,
.web-imgs img {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: 8px;
}

.web {
  padding: 12px;
}

.web h2 {
  margin: 4px 0;
  font-size: 1.15rem;
}
</style>
