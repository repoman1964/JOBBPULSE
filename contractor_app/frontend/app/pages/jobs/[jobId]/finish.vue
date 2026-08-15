<script setup lang="ts">
import type { Job, MediaAsset } from '~/types/domain'
import { categoryLabel, meetsMinimums } from '~/utils/jobStatus'

const route = useRoute()
const api = useApi()
const { session } = useAuthSession()

const jobId = computed(() => String(route.params.jobId))
const job = ref<Job | null>(null)
const voice = ref<MediaAsset | null>(null)
const loading = ref(true)
const error = ref('')
const playError = ref('')
const submitting = ref(false)
const submitted = ref(false)

const recorderState = ref<'idle' | 'recording' | 'complete'>('idle')
const elapsed = ref(0)
const audioUrl = ref<string | null>(null)
const mediaRecorder = ref<MediaRecorder | null>(null)
const chunks = ref<Blob[]>([])
const timer = ref<ReturnType<typeof setInterval> | null>(null)
const fileFallback = ref<HTMLInputElement | null>(null)
const audioEl = ref<HTMLAudioElement | null>(null)
const isPlaying = ref(false)

const minimums = computed(() => session.value?.company.photoMinimums || { before: 2, progress: 0, after: 2 })
const photosOk = computed(() =>
  job.value ? meetsMinimums(job.value.counts, minimums.value) : false,
)
const canSubmit = computed(
  () => photosOk.value && (recorderState.value === 'complete' || !!voice.value) && !submitting.value,
)

const playableUrl = computed(() => audioUrl.value || voice.value?.url || null)

function pickRecorderMime(): string {
  if (typeof MediaRecorder === 'undefined') return ''
  const candidates = [
    'audio/webm;codecs=opus',
    'audio/webm',
    'audio/mp4',
    'audio/ogg;codecs=opus',
    'audio/ogg',
  ]
  return candidates.find((t) => MediaRecorder.isTypeSupported(t)) || ''
}

function blobToDataUrl(blob: Blob): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(reader.error || new Error('Could not read recording'))
    reader.readAsDataURL(blob)
  })
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    job.value = await api.getJob(jobId.value)
    voice.value = await api.getVoice(jobId.value)
    if (voice.value) {
      recorderState.value = 'complete'
      // Restore playable URL from mock persistence (data: URLs survive reload)
      if (voice.value.url && !audioUrl.value) {
        audioUrl.value = voice.value.url
      }
      if (voice.value.durationMs) {
        elapsed.value = Math.max(1, Math.round(voice.value.durationMs / 1000))
      }
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load finish page.'
  } finally {
    loading.value = false
  }
}

function formatTime(sec: number) {
  const m = Math.floor(sec / 60)
  const s = sec % 60
  return `${m}:${String(s).padStart(2, '0')}`
}

async function startRecording() {
  error.value = ''
  playError.value = ''
  if (!import.meta.client || !navigator.mediaDevices?.getUserMedia) {
    error.value = 'Audio recording is not supported on this browser. Upload an audio file instead.'
    fileFallback.value?.click()
    return
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    const mime = pickRecorderMime()
    const rec = new MediaRecorder(stream, mime ? { mimeType: mime } : undefined)
    chunks.value = []
    rec.ondataavailable = (e) => {
      if (e.data && e.data.size > 0) chunks.value.push(e.data)
    }
    rec.onstop = async () => {
      stream.getTracks().forEach((t) => t.stop())
      try {
        if (!chunks.value.length) {
          error.value = 'No audio was captured. Try again or upload a file.'
          recorderState.value = 'idle'
          return
        }
        const blob = new Blob(chunks.value, { type: rec.mimeType || mime || 'audio/webm' })
        // data: URL so mock persistence + playback work after navigation
        const dataUrl = await blobToDataUrl(blob)
        audioUrl.value = dataUrl
        recorderState.value = 'complete'
        await uploadVoice(blob, rec.mimeType || mime || 'audio/webm', dataUrl)
      } catch (e) {
        error.value = e instanceof Error ? e.message : 'Could not save recording.'
        recorderState.value = 'idle'
      }
    }
    mediaRecorder.value = rec
    // timeslice helps some mobile browsers flush chunks
    rec.start(250)
    recorderState.value = 'recording'
    elapsed.value = 0
    timer.value = setInterval(() => {
      elapsed.value += 1
      if (elapsed.value >= 120) stopRecording()
    }, 1000)
  } catch {
    error.value = 'Could not access the microphone. Upload an audio file instead.'
    fileFallback.value?.click()
  }
}

function stopRecording() {
  if (timer.value) clearInterval(timer.value)
  timer.value = null
  const rec = mediaRecorder.value
  if (!rec) return
  try {
    if (rec.state === 'recording') {
      rec.requestData?.()
      rec.stop()
    }
  } catch {
    // ignore
  }
  mediaRecorder.value = null
}

function reRecord() {
  stopPlayback()
  audioUrl.value = null
  voice.value = null
  recorderState.value = 'idle'
  elapsed.value = 0
  playError.value = ''
}

function stopPlayback() {
  if (audioEl.value) {
    audioEl.value.pause()
    audioEl.value.currentTime = 0
    audioEl.value = null
  }
  isPlaying.value = false
}

async function playRecording() {
  playError.value = ''
  const url = playableUrl.value
  if (!url) {
    playError.value =
      'Nothing to play yet. Record a new description (seed demos may not include a real audio file).'
    return
  }
  // blob: URLs from a previous session are dead after reload
  if (url.startsWith('blob:') && !audioUrl.value?.startsWith('blob:')) {
    // kept for safety; usually we now store data:
  }
  try {
    stopPlayback()
    const audio = new Audio(url)
    audioEl.value = audio
    audio.onended = () => {
      isPlaying.value = false
    }
    audio.onerror = () => {
      isPlaying.value = false
      playError.value =
        'Could not play this recording on this device. Re-record or upload a different audio file.'
    }
    isPlaying.value = true
    await audio.play()
  } catch (e) {
    isPlaying.value = false
    playError.value =
      e instanceof Error
        ? `Playback failed: ${e.message}`
        : 'Playback failed. Re-record and try again.'
  }
}

async function uploadVoice(blob: Blob, mimeType: string, durableUrl?: string) {
  const sessionUpload = await api.createVoiceUploadSession(jobId.value, {
    mimeType,
    byteSize: blob.size,
    durationMs: elapsed.value * 1000 || 1000,
  })
  const url = durableUrl || (await blobToDataUrl(blob))
  audioUrl.value = url
  voice.value = await api.completeVoiceUpload(jobId.value, sessionUpload.mediaId, url)
  job.value = await api.getJob(jobId.value)
}

async function onAudioFile(ev: Event) {
  const input = ev.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  playError.value = ''
  try {
    const dataUrl = await blobToDataUrl(file)
    audioUrl.value = dataUrl
    recorderState.value = 'complete'
    elapsed.value = 30
    await uploadVoice(file, file.type || 'audio/mpeg', dataUrl)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not upload audio file.'
  }
  input.value = ''
}

async function submit() {
  if (!canSubmit.value) return
  submitting.value = true
  error.value = ''
  try {
    const key = `submit-${jobId.value}-${Date.now()}`
    await api.submitJob(jobId.value, { idempotencyKey: key })
    await api.submitJob(jobId.value, { idempotencyKey: key })
    submitted.value = true
    setTimeout(() => navigateTo('/jobs'), 1200)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Submission failed. Try again.'
  } finally {
    submitting.value = false
  }
}

onMounted(load)
onBeforeUnmount(() => {
  if (timer.value) clearInterval(timer.value)
  stopPlayback()
})
</script>

<template>
  <div>
    <JpHeader show-back :back-to="`/jobs/${jobId}`" />
    <main class="app-main">
      <h1 class="page-title">Finish Job</h1>
      <template v-if="job">
        <p class="job-name">{{ job.name }}</p>
        <p class="muted loc">📍 {{ job.locationText }}</p>
        <StatusPill :label="photosOk ? 'Ready to Finish' : 'In Progress'" />

        <div v-if="error" class="banner banner-error" role="alert" style="margin-top: 12px">{{ error }}</div>
        <div v-if="submitted" class="banner" style="margin-top: 12px">
          Job submitted. JobbPulse is creating your content…
        </div>

        <section class="card" style="margin-top: 16px">
          <h2 class="section-label">Photo check</h2>
          <div
            v-for="cat in (['before', 'progress', 'after'] as const)"
            :key="cat"
            class="check-row"
          >
            <span>{{ categoryLabel(cat) }}</span>
            <span class="muted">{{ job.counts[cat] }} photos</span>
            <span
              class="check"
              :class="{ ok: job.counts[cat] >= minimums[cat] }"
              :aria-label="job.counts[cat] >= minimums[cat] ? 'Minimum met' : 'Minimum not met'"
            >✓</span>
          </div>
          <NuxtLink class="link-lime" :to="`/jobs/${jobId}/photos/before`">
            Review Photos ›
          </NuxtLink>
        </section>

        <section class="card" style="margin-top: 12px">
          <h2 class="section-label">Tell us about the job</h2>
          <p class="muted" style="margin-top: 0">
            Briefly describe what the customer needed, what you did, and how it turned out.
          </p>

          <div v-if="recorderState === 'idle'" class="stack">
            <button type="button" class="btn btn-primary" @click="startRecording">
              🎙 Start Recording
            </button>
            <button type="button" class="btn btn-secondary" @click="fileFallback?.click()">
              Upload audio file instead
            </button>
          </div>

          <div v-else-if="recorderState === 'recording'" class="stack">
            <p class="recording-timer">Recording… {{ formatTime(elapsed) }}</p>
            <button type="button" class="btn btn-danger" @click="stopRecording">Stop Recording</button>
          </div>

          <div v-else class="stack">
            <div class="rec-complete">
              <button type="button" class="play-btn" aria-label="Play recording" @click="playRecording">
                {{ isPlaying ? '⏸' : '▶' }}
              </button>
              <div>
                <p class="lime">Recording Complete</p>
                <p class="muted" style="margin: 0">{{ formatTime(elapsed || 30) }}</p>
              </div>
            </div>
            <p v-if="playError" class="field-error" role="alert">{{ playError }}</p>
            <p v-if="!playableUrl" class="muted" style="font-size: 0.85rem; margin: 0">
              This job shows a saved voice flag, but no playable audio file is available. Re-record to test playback.
            </p>
            <div class="row" style="gap: 8px">
              <button
                type="button"
                class="btn btn-primary"
                style="flex: 1"
                :disabled="!playableUrl"
                @click="playRecording"
              >
                {{ isPlaying ? 'Playing…' : 'Play Recording' }}
              </button>
              <button type="button" class="btn btn-secondary" style="flex: 1" @click="reRecord">
                Re-record
              </button>
            </div>
          </div>
        </section>

        <button
          type="button"
          class="btn btn-primary"
          style="margin-top: 16px"
          :disabled="!canSubmit"
          @click="submit"
        >
          {{ submitting ? 'Submitting…' : 'Submit Job' }}
        </button>
        <p class="helper-text">
          <template v-if="canSubmit">Ready to submit</template>
          <template v-else-if="!photosOk">Add required photos before submitting</template>
          <template v-else>Record a short description to submit</template>
        </p>
      </template>
      <p v-else-if="loading" class="muted">Loading…</p>

      <input
        ref="fileFallback"
        type="file"
        accept="audio/*"
        class="sr-only"
        @change="onAudioFile"
      />
    </main>
  </div>
</template>

<style scoped>
.job-name {
  margin: 4px 0;
  font-size: 1.15rem;
  font-weight: 700;
}

.loc {
  margin: 0 0 10px;
}

.check-row {
  display: grid;
  grid-template-columns: 1fr auto auto;
  gap: 12px;
  align-items: center;
  padding: 12px 0;
  border-bottom: 1px solid var(--jp-card-border);
}

.check-row:last-of-type {
  border-bottom: none;
}

.check {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: 2px solid var(--jp-card-border);
  color: transparent;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
}

.check.ok {
  border-color: var(--jp-accent);
  color: var(--jp-accent);
  background: var(--jp-accent-dim);
}

.recording-timer {
  text-align: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--jp-danger);
}

.rec-complete {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: var(--jp-bg-elevated);
  border-radius: 12px;
}

.play-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  border: none;
  background: var(--jp-accent);
  color: #0a0a0a;
  font-size: 1.1rem;
  cursor: pointer;
}

.lime {
  margin: 0;
  color: var(--jp-accent);
  font-weight: 700;
}
</style>
