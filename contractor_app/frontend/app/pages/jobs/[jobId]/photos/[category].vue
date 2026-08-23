<script setup lang="ts">
import type { Job, MediaAsset, PhotoCategory } from '~/types/domain'
import { categoryLabel } from '~/utils/jobStatus'
import { putToPresignedUrl } from '~/utils/presignedUpload'

const route = useRoute()
const api = useApi()
const { session } = useAuthSession()

const jobId = computed(() => String(route.params.jobId))
const category = computed(() => String(route.params.category) as PhotoCategory)

const job = ref<Job | null>(null)
const media = ref<MediaAsset[]>([])
const loading = ref(true)
const error = ref('')
const viewer = ref<MediaAsset | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
const uploading = ref(false)

const minimums = computed(() => session.value?.company.photoMinimums || { before: 2, progress: 0, after: 2 })
const minMet = computed(() => {
  const min = minimums.value[category.value] ?? 0
  return media.value.length >= min
})

const categories: PhotoCategory[] = ['before', 'progress', 'after']

async function load() {
  loading.value = true
  error.value = ''
  try {
    job.value = await api.getJob(jobId.value)
    media.value = await api.listMedia(jobId.value, category.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load photos.'
  } finally {
    loading.value = false
  }
}

function switchCategory(cat: PhotoCategory) {
  navigateTo(`/jobs/${jobId.value}/photos/${cat}`)
}

async function toggleFavorite(m: MediaAsset) {
  const updated = await api.updateMedia(jobId.value, m.id, { isFavorite: !m.isFavorite })
  media.value = media.value.map((x) => (x.id === m.id ? updated : x))
  if (viewer.value?.id === m.id) viewer.value = updated
}

async function movePhoto(m: MediaAsset, next: PhotoCategory) {
  await api.updateMedia(jobId.value, m.id, { photoCategory: next })
  viewer.value = null
  await load()
}

async function deletePhoto(m: MediaAsset) {
  if (!confirm('Delete this photo? You can re-add it later if needed.')) return
  await api.deleteMedia(jobId.value, m.id)
  viewer.value = null
  await load()
}

async function onFilesSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const files = input.files
  if (!files?.length) return
  uploading.value = true
  try {
    for (const file of Array.from(files)) {
      if (!file.type.startsWith('image/')) continue
      const mimeType = file.type || 'image/jpeg'
      const sessionUpload = await api.createPhotoUploadSession(jobId.value, category.value, {
        mimeType,
        byteSize: file.size,
        filename: file.name,
      })
      await putToPresignedUrl(sessionUpload.uploadUrl, file, mimeType)
      const objectUrl = URL.createObjectURL(file)
      await api.completeMediaUpload(jobId.value, sessionUpload.mediaId, objectUrl)
    }
    await load()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Photo upload failed.'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

onMounted(load)
watch(category, load)
</script>

<template>
  <div>
    <JpHeader show-back :back-to="`/jobs/${jobId}`" />
    <main class="app-main">
      <div class="row-between" style="align-items: flex-start">
        <div>
          <h1 class="page-title" style="font-size: 1.45rem">
            {{ categoryLabel(category) }} Photos
          </h1>
          <p v-if="job" class="muted" style="margin: 0">{{ job.name }}</p>
        </div>
        <div class="meta">
          <strong>{{ media.length }}</strong>
          <span class="dim">photos</span>
          <StatusPill v-if="minMet" label="Minimum met" />
        </div>
      </div>

      <div class="switcher" role="tablist" aria-label="Photo category">
        <button
          v-for="cat in categories"
          :key="cat"
          type="button"
          role="tab"
          :aria-selected="cat === category"
          :class="{ active: cat === category }"
          @click="switchCategory(cat)"
        >
          {{ categoryLabel(cat) }}
        </button>
      </div>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <p v-if="loading" class="muted">Loading…</p>
      <p v-else-if="uploading" class="banner">Uploading…</p>

      <div v-else class="grid">
        <button
          v-for="m in media"
          :key="m.id"
          type="button"
          class="thumb"
          @click="viewer = m"
        >
          <img :src="m.thumbnailUrl || m.url" :alt="`${categoryLabel(category)} photo`" />
          <span
            class="fav"
            :class="{ on: m.isFavorite }"
            role="img"
            :aria-label="m.isFavorite ? 'Favorite' : 'Not favorite'"
            @click.stop="toggleFavorite(m)"
          >★</span>
        </button>
      </div>

      <div class="bottom-add">
        <button type="button" class="btn btn-primary" @click="fileInput?.click()">
          📷 Add {{ categoryLabel(category) }} Photos
        </button>
      </div>

      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        capture="environment"
        class="sr-only"
        @change="onFilesSelected"
      />

      <div v-if="viewer" class="viewer" role="dialog" aria-modal="true" aria-label="Photo viewer">
        <button type="button" class="viewer-close icon-btn" aria-label="Close" @click="viewer = null">✕</button>
        <img :src="viewer.url" :alt="`${categoryLabel(category)} full photo`" />
        <div class="viewer-actions">
          <button type="button" class="btn btn-secondary" @click="toggleFavorite(viewer)">
            {{ viewer.isFavorite ? 'Unfavorite' : 'Favorite' }}
          </button>
          <label class="move-label">
            Move to
            <select
              :value="viewer.photoCategory || category"
              @change="movePhoto(viewer, ($event.target as HTMLSelectElement).value as PhotoCategory)"
            >
              <option value="before">Before</option>
              <option value="progress">In-Progress</option>
              <option value="after">After</option>
            </select>
          </label>
          <button type="button" class="btn btn-danger" @click="deletePhoto(viewer)">Delete</button>
        </div>
      </div>
    </main>
  </div>
</template>

<style scoped>
.meta {
  text-align: right;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  font-size: 0.85rem;
}

.switcher {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
  margin: 14px 0;
  background: var(--jp-card);
  padding: 4px;
  border-radius: 12px;
  border: 1px solid var(--jp-card-border);
}

.switcher button {
  min-height: 40px;
  border: none;
  background: transparent;
  color: var(--jp-text-muted);
  border-radius: 10px;
  font-weight: 700;
  cursor: pointer;
}

.switcher button.active {
  background: var(--jp-accent);
  color: #0a0a0a;
}

.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  padding-bottom: 96px;
}

.thumb {
  position: relative;
  border: none;
  padding: 0;
  border-radius: 12px;
  overflow: hidden;
  background: #111;
  cursor: pointer;
  aspect-ratio: 1;
}

.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.fav {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #666;
  font-size: 1rem;
}

.fav.on {
  color: var(--jp-accent);
}

.bottom-add {
  position: sticky;
  bottom: calc(12px + var(--jp-safe-bottom));
  padding-top: 8px;
}

.viewer {
  position: fixed;
  inset: 0;
  z-index: 50;
  background: rgba(0, 0, 0, 0.94);
  display: flex;
  flex-direction: column;
  max-width: var(--jp-max-width);
  margin: 0 auto;
  padding: calc(12px + var(--jp-safe-top)) 12px calc(16px + var(--jp-safe-bottom));
}

.viewer img {
  flex: 1;
  object-fit: contain;
  width: 100%;
  min-height: 0;
}

.viewer-close {
  align-self: flex-end;
  width: 44px;
  height: 44px;
  border: none;
  background: transparent;
  color: white;
  font-size: 1.25rem;
  cursor: pointer;
}

.viewer-actions {
  display: grid;
  gap: 8px;
  margin-top: 12px;
}

.move-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  min-height: 48px;
  padding: 0 12px;
  border: 1px solid var(--jp-card-border);
  border-radius: 12px;
  color: var(--jp-text-muted);
}

.move-label select {
  min-height: 44px;
  background: transparent;
  border: none;
  color: var(--jp-text);
}
</style>
