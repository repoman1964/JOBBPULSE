<script setup lang="ts">
import type { Job, MediaAsset, PhotoCategory } from '~/types/domain'
import { categoryLabel, missingMinimums, statusLabel } from '~/utils/jobStatus'
import { putToPresignedUrl } from '~/utils/presignedUpload'

const route = useRoute()
const api = useApi()
const { session } = useAuthSession()

const jobId = computed(() => String(route.params.jobId))
const job = ref<Job | null>(null)
const media = ref<MediaAsset[]>([])
const loading = ref(true)
const error = ref('')
const fileInput = ref<HTMLInputElement | null>(null)
const pendingCategory = ref<PhotoCategory>('before')
const uploading = ref(false)
const confirmDelete = ref(false)
const deleting = ref(false)

const minimums = computed(() => session.value?.company.photoMinimums || { before: 2, progress: 0, after: 2 })

const missing = computed(() =>
  job.value ? missingMinimums(job.value.counts, minimums.value) : [],
)

const canFinish = computed(() => job.value && missing.value.length === 0)

const suggested = computed<PhotoCategory>(() => {
  if (!job.value) return 'before'
  if (job.value.counts.before < minimums.value.before) return 'before'
  if (job.value.counts.after < minimums.value.after) return 'after'
  return 'progress'
})

const categories: PhotoCategory[] = ['before', 'progress', 'after']

function thumbs(category: PhotoCategory) {
  return media.value.filter((m) => m.photoCategory === category).slice(0, 2)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    job.value = await api.getJob(jobId.value)
    media.value = await api.listMedia(jobId.value)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load job.'
  } finally {
    loading.value = false
  }
}

function openPicker(category: PhotoCategory) {
  pendingCategory.value = category
  fileInput.value?.click()
}

async function onFilesSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const files = input.files
  if (!files?.length) return
  uploading.value = true
  error.value = ''
  try {
    for (const file of Array.from(files)) {
      if (!file.type.startsWith('image/')) continue
      const mimeType = file.type || 'image/jpeg'
      const sessionUpload = await api.createPhotoUploadSession(jobId.value, pendingCategory.value, {
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
    error.value = e instanceof Error ? e.message : 'Photo upload failed. Try again.'
  } finally {
    uploading.value = false
    input.value = ''
  }
}

async function removeJob() {
  if (!job.value) return
  deleting.value = true
  error.value = ''
  try {
    await api.deleteJob(job.value.id)
    await navigateTo('/jobs')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not delete this job.'
    confirmDelete.value = false
  } finally {
    deleting.value = false
  }
}

const canDelete = computed(
  () => job.value && job.value.publicStatus !== 'publishing',
)

onMounted(load)
</script>

<template>
  <div>
    <JpHeader show-back back-to="/jobs" />
    <main class="app-main">
      <div v-if="loading" class="muted">Loading job…</div>
      <div v-else-if="error && !job" class="banner banner-error" role="alert">{{ error }}</div>
      <template v-else-if="job">
        <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
        <div v-if="uploading" class="banner">Uploading photos…</div>

        <h1 class="job-title">{{ job.name }}</h1>
        <p class="muted loc">
          <span aria-hidden="true">📍</span>
          {{ job.locationText }}
        </p>
        <StatusPill :label="statusLabel(job.publicStatus, job)" />

        <div class="stack-lg" style="margin-top: 16px">
          <section
            v-for="cat in categories"
            :key="cat"
            class="card category-card"
            :class="{ 'category-card--suggested': suggested === cat && job.publicStatus === 'active' }"
          >
            <div class="row-between">
              <div>
                <h2 class="cat-title">{{ categoryLabel(cat) }}</h2>
                <p class="cat-count dim">{{ job.counts[cat] }} photos</p>
              </div>
              <NuxtLink class="link-lime" :to="`/jobs/${job.id}/photos/${cat}`">
                Open {{ categoryLabel(cat) }} Gallery ›
              </NuxtLink>
            </div>

            <div v-if="thumbs(cat).length" class="thumb-row">
              <img
                v-for="m in thumbs(cat)"
                :key="m.id"
                :src="m.thumbnailUrl || m.url"
                :alt="`${categoryLabel(cat)} photo`"
              />
            </div>
            <div v-else class="empty-thumbs">
              <span aria-hidden="true">📷</span>
              <p>No {{ categoryLabel(cat) }} photos yet</p>
            </div>

            <button
              type="button"
              class="btn"
              :class="suggested === cat ? 'btn-primary' : 'btn-outline-lime'"
              @click="openPicker(cat)"
            >
              📷 Add {{ categoryLabel(cat) }} Photos
            </button>
          </section>
        </div>

        <div style="margin-top: 16px">
          <NuxtLink
            v-if="canFinish"
            class="btn btn-primary"
            :to="`/jobs/${job.id}/finish`"
          >
            Finish Job
          </NuxtLink>
          <button v-else type="button" class="btn btn-secondary" disabled>
            Finish Job
          </button>
          <p v-if="!canFinish" class="helper-text">
            <template v-if="missing.includes('before') && missing.includes('after')">
              Add before and after photos to finish
            </template>
            <template v-else-if="missing.includes('before')">Add before photos to finish</template>
            <template v-else-if="missing.includes('after')">Add after photos to finish</template>
            <template v-else-if="missing.includes('progress')">Add In-Progress photos to finish</template>
          </p>
          <p v-else-if="job.publicStatus === 'processing'" class="helper-text">
            JobbPulse is creating your content. We’ll let you know when it’s ready for approval.
          </p>
          <p v-else-if="job.publicStatus === 'ready_for_approval'" class="helper-text">
            <NuxtLink class="link-lime" :to="`/jobs/${job.id}/approval`">Review content →</NuxtLink>
          </p>
        </div>

        <section class="delete-job" style="margin-top: 28px">
          <button
            v-if="!confirmDelete"
            type="button"
            class="btn btn-danger"
            :disabled="!canDelete || deleting"
            @click="confirmDelete = true"
          >
            Delete job
          </button>
          <div v-else class="card stack">
            <p class="helper-text" style="margin: 0">
              Hide <strong>{{ job.name }}</strong> from your job list? Photos and published
              content stay on file.
            </p>
            <button
              type="button"
              class="btn btn-danger"
              :disabled="deleting"
              @click="removeJob"
            >
              {{ deleting ? 'Deleting…' : 'Yes, delete this job' }}
            </button>
            <button type="button" class="btn btn-secondary" :disabled="deleting" @click="confirmDelete = false">
              Cancel
            </button>
          </div>
        </section>
      </template>

      <input
        ref="fileInput"
        type="file"
        accept="image/*"
        multiple
        capture="environment"
        class="sr-only"
        @change="onFilesSelected"
      />
    </main>
  </div>
</template>

<style scoped>
.job-title {
  margin: 8px 0 4px;
  font-size: 1.5rem;
  font-weight: 800;
}

.loc {
  margin: 0 0 10px;
}

.cat-title {
  margin: 0;
  font-size: 0.95rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

.cat-count {
  margin: 2px 0 0;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.category-card--suggested {
  border-color: rgba(200, 240, 0, 0.55);
  box-shadow: 0 0 0 1px rgba(200, 240, 0, 0.2);
}

.thumb-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  margin: 12px 0;
}

.thumb-row img {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  border-radius: 12px;
}

.empty-thumbs {
  margin: 12px 0;
  border: 1px dashed var(--jp-card-border);
  border-radius: 12px;
  min-height: 100px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--jp-text-dim);
  gap: 6px;
}

.empty-thumbs p {
  margin: 0;
  font-size: 0.9rem;
}
</style>
