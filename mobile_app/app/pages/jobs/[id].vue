<template>
  <div>
    <header class="top-bar">
      <NuxtLink to="/" class="muted">← Jobs</NuxtLink>
      <div class="top-title">{{ job?.title || 'Job' }}</div>
      <button type="button" class="linkish" :disabled="!job || savingMeta" @click="saveMeta">
        {{ savingMeta ? '…' : 'Save' }}
      </button>
    </header>

    <div v-if="loading" class="page-body">
      <p class="muted">Loading job…</p>
    </div>

    <div v-else-if="!job" class="page-body">
      <div class="card">
        <p class="error-text">{{ error || 'Job not found.' }}</p>
        <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/')">Back home</button>
      </div>
    </div>

    <div v-else class="page-body">
      <!-- Visual timeline -->
      <div class="card timeline-card" style="margin-bottom: 12px;">
        <div class="timeline">
          <div
            v-for="(step, i) in job.timeline"
            :key="step.key"
            class="t-step"
            :class="step.status"
          >
            <div class="t-rail">
              <div class="t-dot" />
              <div v-if="i < job.timeline.length - 1" class="t-line" />
            </div>
            <div class="t-body">
              <div class="t-label">{{ step.label }}</div>
              <div v-if="step.status === 'current'" class="t-hint">You’re here</div>
              <div v-else-if="step.status === 'locked'" class="t-hint">Coming next</div>
            </div>
          </div>
        </div>
      </div>

      <div class="card next-banner" style="margin-bottom: 12px;">
        <div class="muted" style="font-size: 12px; font-weight: 600; text-transform: uppercase;">
          Next step
        </div>
        <div style="font-weight: 700; margin: 4px 0;">{{ job.next_action.label }}</div>
        <div class="muted" style="font-size: 13px;">{{ job.next_action.reason }}</div>
        <p v-if="job.next_action.optional_tip" class="tip-banner">
          {{ job.next_action.optional_tip }}
        </p>
        <div class="counts-row">
          <span>{{ job.photo_counts.before }} before <em class="opt">(optional)</em></span>
          <span>{{ job.photo_counts.after }} after <em class="req-label">(required)</em></span>
        </div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <label class="field-label">Job name <span class="req">*</span></label>
        <input v-model="editTitle" class="field-input" type="text" maxlength="200" />
        <p class="privacy-note">Private to you — not used in marketing or AI posts.</p>
        <div class="muted" style="margin-top: 10px; font-size: 13px;">
          Status: <strong>{{ statusLabel(job.status) }}</strong>
          <template v-if="job.location_display || job.city">
            · Area: {{ job.location_display || job.city }}
          </template>
        </div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div class="field-label">Photo stage</div>
        <div class="stage-row">
          <button
            v-for="s in stages"
            :key="s.key"
            type="button"
            :class="['stage-pill', { on: activeStage === s.key }]"
            @click="activeStage = s.key"
          >
            {{ s.label }}
            <span class="count-chip">{{ s.key === 'before' ? job.photo_counts.before : job.photo_counts.after }}</span>
          </button>
        </div>

        <p class="muted" style="margin: 12px 0; font-size: 13px;">
          {{ stageHint }}
        </p>
        <p v-if="!job.photo_counts.before && job.photo_counts.after" class="tip-banner" style="margin-top: 0;">
          No before photos — that’s OK. After + voice still complete the job.
        </p>

        <input
          ref="fileInput"
          type="file"
          accept="image/*"
          capture="environment"
          multiple
          style="display: none;"
          @change="onFilesSelected"
        />

        <button
          class="btn btn-primary btn-block"
          type="button"
          :disabled="media.uploading.value"
          @click="pickPhotos"
        >
          {{ media.uploading.value ? media.progressLabel.value || 'Uploading…' : captureCta }}
        </button>

        <button
          class="btn btn-block"
          type="button"
          style="margin-top: 10px; background: #e8eef5; color: var(--jp-primary);"
          :disabled="media.uploading.value"
          @click="pickFromLibrary"
        >
          Choose from library
        </button>

        <p v-if="media.uploadError.value" class="error-text">{{ media.uploadError.value }}</p>
        <p v-if="uploadNote" class="muted" style="margin-top: 10px; font-size: 13px;">{{ uploadNote }}</p>
      </div>

      <div v-for="group in photoGroups" :key="group.key" class="card" style="margin-bottom: 12px;">
        <div class="group-head">
          <span style="font-weight: 600;">{{ group.label }}</span>
          <span class="muted" style="font-size: 13px;">{{ group.items.length }}</span>
        </div>
        <div v-if="!group.items.length" class="muted" style="font-size: 13px; margin-top: 8px;">
          No {{ group.label.toLowerCase() }} photos yet.
        </div>
        <div v-else class="photo-list">
          <div v-for="(m, idx) in group.items" :key="m.id" class="photo-row">
            <div class="thumb">
              <img v-if="m.url" :src="m.url" :alt="m.stage_label" />
              <div v-else class="photo-fallback">Photo</div>
            </div>
            <div class="photo-meta">
              <div class="muted" style="font-size: 12px;">
                {{ m.is_primary ? 'Primary · ' : '' }}#{{ idx + 1 }}
              </div>
              <div class="reorder-btns">
                <button
                  type="button"
                  class="mini"
                  :disabled="idx === 0 || reordering"
                  @click="moveInStage(group.key, idx, -1)"
                >
                  ↑
                </button>
                <button
                  type="button"
                  class="mini"
                  :disabled="idx === group.items.length - 1 || reordering"
                  @click="moveInStage(group.key, idx, 1)"
                >
                  ↓
                </button>
              </div>
              <div class="photo-actions">
                <button type="button" class="mini" :disabled="m.is_primary" @click="setPrimary(m.id)">
                  {{ m.is_primary ? 'Primary' : 'Primary' }}
                </button>
                <button
                  type="button"
                  class="mini"
                  @click="relabel(m.id, m.stage_label === 'before' ? 'after' : 'before')"
                >
                  → {{ m.stage_label === 'before' ? 'After' : 'Before' }}
                </button>
                <button type="button" class="mini danger" @click="removePhoto(m.id)">Delete</button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="card" style="margin-bottom: 24px;">
        <p class="muted" style="margin: 0 0 12px; font-size: 13px;">
          This job is saved on the server. Close the app anytime and continue later from Your jobs.
        </p>
        <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/')">
          Finish later
        </button>
        <button
          class="btn btn-block"
          type="button"
          style="margin-top: 10px; background: #fee2e2; color: #991b1b;"
          @click="archive"
        >
          Archive job
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { JobDetail, MediaAsset } from '~/composables/useJobs'
import type { StageLabel } from '~/composables/useJobMedia'

const route = useRoute()
const api = useApi()
const media = useJobMedia()
const { statusLabel } = useJobs()

const jobId = computed(() => String(route.params.id))
const job = ref<JobDetail | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const editTitle = ref('')
const savingMeta = ref(false)
const reordering = ref(false)
const uploadNote = ref('')
const fileInput = ref<HTMLInputElement | null>(null)

const stages = [
  { key: 'before' as StageLabel, label: 'Before (optional)' },
  { key: 'after' as StageLabel, label: 'After (required)' },
]

const activeStage = ref<StageLabel>('after')

const stageHint = computed(() => {
  if (activeStage.value === 'before') {
    return 'Optional: capture the site before work if you can. Skipping is fine.'
  }
  return 'Required: photos of the completed work. Then you’ll record a short voice summary.'
})

const captureCta = computed(() =>
  activeStage.value === 'before' ? 'Add before photos (optional)' : 'Add after photos (required)',
)

const photoGroups = computed(() => {
  const items = job.value?.media || []
  const by = (label: string) =>
    items
      .filter((m) => m.stage_label === label)
      .slice()
      .sort((a, b) => a.display_order - b.display_order || a.created_at.localeCompare(b.created_at))
  return [
    { key: 'before' as StageLabel, label: 'Before', items: by('before') },
    { key: 'after' as StageLabel, label: 'After', items: by('after') },
  ]
})

function applyJob(data: JobDetail) {
  job.value = data
  editTitle.value = data.title
}

async function loadJob() {
  loading.value = true
  error.value = null
  try {
    const data = (await api.getJob(jobId.value)) as JobDetail
    applyJob(data)
  } catch (e: any) {
    error.value = e?.message || 'Failed to load job'
    job.value = null
  } finally {
    loading.value = false
  }
}

async function saveMeta() {
  if (!job.value || savingMeta.value) return
  const name = editTitle.value.trim()
  if (!name) {
    uploadNote.value = 'Job name is required.'
    return
  }
  savingMeta.value = true
  try {
    const data = (await api.updateJob(job.value.id, { title: name })) as JobDetail
    applyJob(data)
    uploadNote.value = 'Saved.'
  } catch (e: any) {
    error.value = e?.message || 'Could not save'
  } finally {
    savingMeta.value = false
  }
}

function pickPhotos() {
  if (fileInput.value) {
    fileInput.value.setAttribute('capture', 'environment')
    fileInput.value.click()
  }
}

function pickFromLibrary() {
  if (fileInput.value) {
    fileInput.value.removeAttribute('capture')
    fileInput.value.click()
  }
}

async function onFilesSelected(ev: Event) {
  const input = ev.target as HTMLInputElement
  const files = input.files
  if (!files?.length || !job.value) return

  uploadNote.value = ''
  try {
    const updated = (await media.uploadMany(
      job.value.id,
      files,
      activeStage.value,
    )) as JobDetail
    applyJob(updated)
    uploadNote.value = `Uploaded ${files.length} photo${files.length === 1 ? '' : 's'}.`
  } catch (e: any) {
    uploadNote.value = e?.message || 'Upload failed'
  } finally {
    input.value = ''
  }
}

async function moveInStage(stage: StageLabel, index: number, delta: number) {
  if (!job.value || reordering.value) return
  const group = photoGroups.value.find((g) => g.key === stage)
  if (!group) return
  const next = index + delta
  if (next < 0 || next >= group.items.length) return

  const stageIds = group.items.map((m) => m.id)
  const tmp = stageIds[index]
  stageIds[index] = stageIds[next]
  stageIds[next] = tmp

  // Full order: before block then after block (or preserve other stages none)
  const beforeIds =
    stage === 'before' ? stageIds : photoGroups.value.find((g) => g.key === 'before')!.items.map((m) => m.id)
  const afterIds =
    stage === 'after' ? stageIds : photoGroups.value.find((g) => g.key === 'after')!.items.map((m) => m.id)
  const fullOrder = [...beforeIds, ...afterIds]

  reordering.value = true
  try {
    const updated = (await media.reorder(job.value.id, fullOrder)) as JobDetail
    applyJob(updated)
  } catch (e: any) {
    uploadNote.value = e?.message || 'Could not reorder'
  } finally {
    reordering.value = false
  }
}

async function relabel(mediaId: string, stage: string) {
  try {
    await api.updateMedia(mediaId, { stage_label: stage })
    await loadJob()
  } catch (e: any) {
    uploadNote.value = e?.message || 'Could not update label'
  }
}

async function setPrimary(mediaId: string) {
  try {
    await api.setPrimaryMedia(mediaId)
    await loadJob()
  } catch (e: any) {
    uploadNote.value = e?.message || 'Could not set primary'
  }
}

async function removePhoto(mediaId: string) {
  if (!confirm('Delete this photo?')) return
  try {
    await api.deleteMedia(mediaId)
    await loadJob()
  } catch (e: any) {
    uploadNote.value = e?.message || 'Could not delete'
  }
}

async function archive() {
  if (!job.value || !confirm('Archive this job?')) return
  try {
    await api.archiveJob(job.value.id)
    await navigateTo('/')
  } catch (e: any) {
    uploadNote.value = e?.message || 'Could not archive'
  }
}

onMounted(async () => {
  const qStage = String(route.query.stage || '')
  if (qStage === 'before' || qStage === 'after') {
    activeStage.value = qStage
  }
  await loadJob()
  if (!route.query.stage && job.value) {
    // Default to required after stage unless they only have befores and no afters
    if (job.value.next_action.action === 'add_after_photos') activeStage.value = 'after'
    else if (job.value.next_action.action === 'record_voice_summary') activeStage.value = 'after'
    else activeStage.value = 'after'
  }
})
</script>

<style scoped>
.top-bar {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  background: var(--jp-surface);
  border-bottom: 1px solid var(--jp-border);
  position: sticky;
  top: 0;
  z-index: 20;
}
.top-title {
  font-weight: 600;
  font-size: 15px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 50%;
}
.linkish {
  border: none;
  background: none;
  color: var(--jp-primary);
  font-weight: 600;
  cursor: pointer;
}
.timeline {
  display: flex;
  flex-direction: column;
  gap: 0;
}
.t-step {
  display: flex;
  gap: 12px;
  min-height: 44px;
}
.t-rail {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 16px;
}
.t-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #cbd5e1;
  border: 2px solid #e2e8f0;
  flex-shrink: 0;
  margin-top: 2px;
}
.t-line {
  width: 2px;
  flex: 1;
  background: #e2e8f0;
  min-height: 20px;
}
.t-step.complete .t-dot {
  background: var(--jp-success);
  border-color: var(--jp-success);
}
.t-step.complete .t-line {
  background: #a7f3d0;
}
.t-step.current .t-dot {
  background: var(--jp-primary);
  border-color: var(--jp-primary);
  box-shadow: 0 0 0 3px rgba(24, 95, 165, 0.25);
}
.t-step.locked .t-dot {
  background: #f8fafc;
  border-color: #e2e8f0;
}
.t-step.optional .t-dot {
  background: #fff;
  border-color: #94a3b8;
  border-style: dashed;
}
.t-step.skipped .t-dot {
  background: #e2e8f0;
  border-color: #cbd5e1;
}
.tip-banner {
  margin: 10px 0 0;
  padding: 8px 10px;
  background: #fff8e6;
  border-radius: 8px;
  font-size: 12px;
  color: #92400e;
  line-height: 1.4;
}
.opt {
  font-style: normal;
  font-weight: 500;
  opacity: 0.75;
}
.req-label {
  font-style: normal;
  font-weight: 600;
  color: var(--jp-primary);
}
.t-label {
  font-weight: 600;
  font-size: 14px;
}
.t-step.current .t-label {
  color: var(--jp-primary);
}
.t-hint {
  font-size: 12px;
  color: var(--jp-text-secondary);
}
.next-banner {
  border-color: #b7d0ea;
  background: #f3f8fc;
}
.counts-row {
  display: flex;
  gap: 12px;
  margin-top: 10px;
  font-size: 13px;
  font-weight: 600;
  color: var(--jp-text-secondary);
}
.field-label {
  display: block;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 6px;
  color: var(--jp-text-secondary);
}
.req {
  color: var(--jp-danger);
}
.field-input {
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--jp-border);
  border-radius: 10px;
  background: #fff;
}
.privacy-note {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--jp-text-secondary);
}
.stage-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.stage-pill {
  border: 1px solid var(--jp-border);
  background: #fff;
  border-radius: 999px;
  padding: 8px 14px;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
  color: var(--jp-text-secondary);
  display: inline-flex;
  align-items: center;
  gap: 6px;
}
.stage-pill.on {
  background: var(--jp-primary);
  border-color: var(--jp-primary);
  color: #fff;
}
.count-chip {
  font-size: 11px;
  opacity: 0.85;
}
.group-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.photo-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 12px;
}
.photo-row {
  display: flex;
  gap: 10px;
  border: 1px solid var(--jp-border);
  border-radius: 10px;
  overflow: hidden;
  background: #f8fafc;
  padding: 8px;
}
.thumb {
  width: 88px;
  height: 88px;
  border-radius: 8px;
  overflow: hidden;
  flex-shrink: 0;
  background: #e2e8f0;
}
.thumb img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}
.photo-fallback {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  color: var(--jp-text-secondary);
}
.photo-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.reorder-btns {
  display: flex;
  gap: 6px;
}
.photo-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}
.mini {
  border: none;
  background: #e8eef5;
  color: var(--jp-primary);
  font-size: 12px;
  font-weight: 600;
  padding: 6px 10px;
  border-radius: 6px;
  cursor: pointer;
}
.mini.danger {
  background: #fee2e2;
  color: #991b1b;
}
.mini:disabled {
  opacity: 0.45;
  cursor: default;
}
.error-text {
  color: var(--jp-danger);
  font-size: 14px;
}
</style>
