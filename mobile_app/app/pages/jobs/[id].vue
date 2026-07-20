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

      <!-- Voice summary -->
      <div
        v-if="showVoiceSection"
        id="voice"
        class="card voice-card"
        style="margin-bottom: 12px;"
      >
        <div class="group-head">
          <span style="font-weight: 600;">Voice summary</span>
          <span class="muted" style="font-size: 13px;">Required</span>
        </div>
        <p class="muted" style="margin: 8px 0 12px; font-size: 13px;">
          Describe the work in 15–60 seconds: problem, what you did, result.
        </p>

        <div v-if="needsRecording" class="recorder">
          <div class="rec-timer">
            <span
              class="rec-dot"
              :class="{ live: recorder.state.value === 'recording' }"
            />
            {{ recorder.formatDuration(recorder.durationMs.value) }}
            <span class="muted" style="font-size: 12px; margin-left: 8px;">
              {{ recorderStateLabel }}
            </span>
          </div>

          <div class="rec-controls">
            <button
              v-if="recorder.state.value === 'idle' || recorder.state.value === 'unsupported'"
              type="button"
              class="btn btn-primary btn-block"
              :disabled="recorder.state.value === 'unsupported' || voiceUpload.uploading.value"
              @click="recorder.start()"
            >
              Start recording
            </button>
            <template v-else-if="recorder.state.value === 'recording'">
              <button type="button" class="btn btn-block rec-pause" @click="recorder.pause()">
                Pause
              </button>
              <button type="button" class="btn btn-primary btn-block" style="margin-top: 8px;" @click="recorder.stop()">
                Stop
              </button>
            </template>
            <template v-else-if="recorder.state.value === 'paused'">
              <button type="button" class="btn btn-primary btn-block" @click="recorder.resume()">
                Resume
              </button>
              <button type="button" class="btn btn-block" style="margin-top: 8px; background: #e8eef5; color: var(--jp-primary);" @click="recorder.stop()">
                Stop
              </button>
            </template>
            <template v-else-if="recorder.state.value === 'stopped'">
              <audio
                v-if="recorder.playbackUrl.value"
                :src="recorder.playbackUrl.value"
                controls
                class="audio-player"
              />
              <button
                type="button"
                class="btn btn-primary btn-block"
                style="margin-top: 10px;"
                :disabled="voiceUpload.uploading.value"
                @click="submitRecording"
              >
                {{ voiceUpload.uploading.value ? (voiceUpload.progressLabel.value || 'Uploading…') : 'Upload & transcribe' }}
              </button>
              <button
                type="button"
                class="btn btn-block"
                style="margin-top: 8px; background: #e8eef5; color: var(--jp-primary);"
                :disabled="voiceUpload.uploading.value"
                @click="recorder.discard()"
              >
                Re-record
              </button>
            </template>
          </div>

          <p v-if="recorder.error.value" class="error-text">{{ recorder.error.value }}</p>
          <p v-if="voiceUpload.uploadError.value" class="error-text">{{ voiceUpload.uploadError.value }}</p>
          <p v-if="voiceNote" class="muted" style="margin-top: 10px; font-size: 13px;">{{ voiceNote }}</p>
        </div>

        <div v-else-if="job.voice">
          <div v-if="job.voice.audio_url" style="margin-bottom: 12px;">
            <audio :src="job.voice.audio_url" controls class="audio-player" />
          </div>

          <div
            v-if="job.voice.transcription_status === 'pending' || job.voice.transcription_status === 'processing'"
            class="muted"
            style="font-size: 13px; margin-bottom: 12px;"
          >
            Transcribing… hang tight.
          </div>
          <div
            v-else-if="job.voice.transcription_status === 'failed'"
            class="error-text"
            style="margin-bottom: 12px;"
          >
            {{ job.voice.transcription_error || 'Transcription failed.' }}
            <button type="button" class="mini" style="margin-left: 8px;" @click="doRetranscribe">
              Retry
            </button>
          </div>

          <template v-if="job.voice.transcription_status === 'completed' || transcriptDraft">
            <label class="field-label">Transcript</label>
            <textarea
              v-model="transcriptDraft"
              class="field-input transcript-area"
              rows="5"
              placeholder="Edit the transcript if needed…"
            />
            <p class="muted" style="margin: 6px 0 0; font-size: 12px;">
              Fix names, materials, or anything the transcript got wrong. AI will use this text.
            </p>
            <button
              type="button"
              class="btn btn-primary btn-block"
              style="margin-top: 12px;"
              :disabled="savingTranscript || !transcriptDraft.trim()"
              @click="saveTranscript"
            >
              {{ savingTranscript ? 'Saving…' : 'Save transcript' }}
            </button>
          </template>

          <div class="voice-actions" style="margin-top: 12px;">
            <button type="button" class="mini" :disabled="voiceUpload.uploading.value" @click="startRerecord">
              Re-record
            </button>
            <button
              v-if="job.voice.transcription_status === 'completed'"
              type="button"
              class="mini"
              :disabled="retranscribing"
              @click="doRetranscribe"
            >
              {{ retranscribing ? '…' : 'Retranscribe' }}
            </button>
          </div>
          <p v-if="voiceNote" class="muted" style="margin-top: 10px; font-size: 13px;">{{ voiceNote }}</p>
        </div>
      </div>

      <div
        v-if="job.next_action.action === 'generate_content'"
        class="card"
        style="margin-bottom: 12px; border-color: #b7d0ea; background: #f3f8fc;"
      >
        <div style="font-weight: 700; margin-bottom: 6px;">Ready to generate</div>
        <p class="muted" style="margin: 0 0 12px; font-size: 13px;">
          Photos and voice are in. Generate draft marketing content for your review.
        </p>
        <p v-if="generateNote" class="muted" style="margin: 0 0 10px; font-size: 13px;">{{ generateNote }}</p>
        <p v-if="generateError" class="error-text" style="margin: 0 0 10px;">{{ generateError }}</p>
        <button
          class="btn btn-primary btn-block"
          type="button"
          :disabled="gen.generating.value"
          @click="doGenerate"
        >
          {{ gen.generating.value ? 'Generating…' : job.next_action.cta || 'Generate content' }}
        </button>
      </div>

      <div
        v-if="job.next_action.action === 'wait_generation'"
        class="card"
        style="margin-bottom: 12px;"
      >
        <div style="font-weight: 700; margin-bottom: 6px;">Generating content…</div>
        <p class="muted" style="margin: 0; font-size: 13px;">{{ job.next_action.reason }}</p>
      </div>

      <!-- Review workspace (Phase 5) -->
      <div
        v-if="showReviewWorkspace"
        class="card"
        style="margin-bottom: 12px; border-color: #c4d9b8; background: #f6faf3;"
      >
        <div style="display: flex; justify-content: space-between; align-items: baseline; gap: 8px;">
          <div style="font-weight: 700;">
            {{ job.status === 'approved' ? 'Approved content' : 'Review content' }}
          </div>
          <span class="muted" style="font-size: 12px;">
            {{ job.status === 'approved' ? 'Ready to publish' : 'Your approval required' }}
          </span>
        </div>
        <p class="muted" style="margin: 6px 0 12px; font-size: 13px;">
          Edit drafts, approve or reject each piece, then mark the job ready when you’re satisfied.
          Nothing publishes without your approval.
        </p>

        <div
          v-if="job.status === 'approved' || job.status === 'published'"
          class="ready-banner"
          style="margin-bottom: 12px;"
        >
          <template v-if="job.status === 'approved'">
            Content is approved. Publish when you’re ready.
          </template>
          <template v-else>
            Live on the JobPulse directory.
          </template>
          <div v-if="canApprove" style="margin-top: 10px; display: flex; flex-direction: column; gap: 8px;">
            <button
              v-if="job.status === 'approved' || !livePublicUrl"
              type="button"
              class="btn btn-primary btn-block"
              :disabled="publish.busy.value"
              @click="doPublish"
            >
              {{ publish.busy.value ? 'Publishing…' : 'Publish' }}
            </button>
            <a
              v-if="livePublicUrl"
              :href="livePublicUrl"
              target="_blank"
              rel="noopener"
              class="btn btn-block"
              style="text-align: center; text-decoration: none; background: #e2e8f0; color: #0f172a;"
            >
              Open live page
            </a>
            <button
              v-if="job.status === 'published' && livePublicUrl"
              type="button"
              class="btn btn-block"
              style="background: transparent; border: 1px solid #cbd5e1; color: #475569;"
              :disabled="publish.busy.value"
              @click="doUnpublish"
            >
              Unpublish from directory
            </button>
            <p class="muted" style="margin: 0; font-size: 12px;">
              One Publish action. Social destinations will use this same button later.
            </p>
          </div>
          <p v-else class="muted" style="margin: 8px 0 0; font-size: 12px;">
            A manager or owner must publish.
          </p>
          <p v-if="publishNote" class="muted" style="margin: 8px 0 0; font-size: 13px; color: #166534;">
            {{ publishNote }}
          </p>
        </div>

        <div v-if="draftWarnings.length" class="tip-banner" style="margin-bottom: 12px;">
          <div v-for="(w, i) in draftWarnings" :key="i">{{ w }}</div>
        </div>
        <div
          v-if="readiness?.soft_warnings?.length"
          class="tip-banner"
          style="margin-bottom: 12px;"
        >
          <div v-for="(w, i) in readiness.soft_warnings" :key="'sw-' + i">{{ w }}</div>
        </div>

        <div v-for="v in draftVariants" :key="v.id" class="draft-card">
          <div class="draft-card-head">
            <div class="draft-type">{{ contentTypeLabel(v.content_type) }}</div>
            <span class="status-pill" :class="'st-' + v.status">{{ variantStatusLabel(v.status) }}</span>
          </div>
          <div v-if="v.title" class="draft-title">{{ v.title }}</div>

          <label class="field-label" style="margin-top: 8px;">Body</label>
          <textarea
            v-model="editBodies[v.id]"
            class="field-input transcript-area"
            rows="5"
            :disabled="v.status === 'superseded' || savingVariantId === v.id"
          />
          <div class="voice-actions" style="margin-top: 8px;">
            <button
              class="btn"
              type="button"
              style="flex: 1;"
              :disabled="savingVariantId === v.id || review.busy.value"
              @click="saveVariant(v)"
            >
              {{ savingVariantId === v.id ? 'Saving…' : 'Save edit' }}
            </button>
            <button
              v-if="canApprove"
              class="btn btn-primary"
              type="button"
              style="flex: 1;"
              :disabled="v.status === 'approved' || review.busy.value"
              @click="approveOne(v)"
            >
              Approve
            </button>
            <button
              v-if="canApprove"
              class="btn"
              type="button"
              style="flex: 1; background: #fee2e2; color: #991b1b;"
              :disabled="v.status === 'rejected' || review.busy.value"
              @click="rejectOne(v)"
            >
              Reject
            </button>
          </div>
          <div v-if="v.call_to_action" class="muted" style="font-size: 12px; margin-top: 8px;">
            CTA: {{ v.call_to_action }}
          </div>
          <div
            v-if="v.hashtags_json?.length"
            class="muted"
            style="font-size: 12px; margin-top: 4px;"
          >
            {{ v.hashtags_json.join(' ') }}
          </div>
        </div>

        <p v-if="!canApprove" class="muted" style="font-size: 12px; margin: 0 0 10px;">
          You can edit drafts. Only a manager or owner can approve or reject.
        </p>

        <div v-if="canApprove && job.status !== 'approved'" style="margin-bottom: 12px;">
          <div v-if="readiness && !readiness.can_approve_job && readiness.blockers.length" class="tip-banner">
            <div style="font-weight: 600; margin-bottom: 4px;">Before job approval:</div>
            <div v-for="(b, i) in readiness.blockers" :key="'b-' + i">• {{ b }}</div>
          </div>
          <button
            class="btn btn-primary btn-block"
            type="button"
            style="margin-top: 10px;"
            :disabled="review.busy.value"
            @click="doApproveAll"
          >
            {{ review.busy.value ? 'Working…' : 'Approve all & mark ready' }}
          </button>
          <button
            class="btn btn-block"
            type="button"
            style="margin-top: 8px;"
            :disabled="review.busy.value || !readiness?.can_approve_job"
            @click="doApproveJob"
          >
            Mark job approved (if rules already met)
          </button>
        </div>

        <div style="margin-top: 4px;">
          <label class="field-label">Regenerate with instruction (optional)</label>
          <textarea
            v-model="regenInstruction"
            class="field-input transcript-area"
            rows="2"
            placeholder="e.g. Focus on curb appeal, shorter captions"
          />
          <button
            class="btn btn-block"
            type="button"
            style="margin-top: 8px;"
            :disabled="gen.generating.value"
            @click="doRegenerate"
          >
            {{ gen.generating.value ? 'Regenerating…' : 'Regenerate drafts' }}
          </button>
        </div>

        <p v-if="generateError" class="error-text" style="margin-top: 10px;">{{ generateError }}</p>
        <p v-if="reviewNote" class="muted" style="margin-top: 8px; font-size: 13px;">{{ reviewNote }}</p>

        <!-- Light version history -->
        <div v-if="generationRuns.length" style="margin-top: 16px; border-top: 1px solid #dce5d6; padding-top: 12px;">
          <button
            type="button"
            class="linkish"
            style="font-weight: 600;"
            @click="showHistory = !showHistory"
          >
            {{ showHistory ? 'Hide' : 'Show' }} version history ({{ generationRuns.length }})
          </button>
          <div v-if="showHistory" style="margin-top: 10px;">
            <div
              v-for="run in generationRuns"
              :key="run.id"
              class="history-run"
            >
              <div style="display: flex; justify-content: space-between; gap: 8px;">
                <strong>v{{ run.variants?.[0]?.version_number || '—' }}</strong>
                <span class="muted" style="font-size: 12px;">{{ run.generation_type }} · {{ run.status }}</span>
              </div>
              <div class="muted" style="font-size: 12px; margin-top: 2px;">
                {{ formatRunDate(run.created_at) }}
                <span v-if="run.user_instruction"> · “{{ run.user_instruction }}”</span>
              </div>
              <button
                type="button"
                class="linkish"
                style="font-size: 13px; margin-top: 4px;"
                @click="toggleRunDetail(run.id)"
              >
                {{ expandedRunId === run.id ? 'Hide variants' : 'View this version' }}
              </button>
              <div v-if="expandedRunId === run.id" style="margin-top: 8px;">
                <div
                  v-for="rv in run.variants || []"
                  :key="rv.id"
                  class="history-variant"
                >
                  <div class="draft-type">
                    {{ contentTypeLabel(rv.content_type) }}
                    <span class="status-pill" :class="'st-' + rv.status" style="margin-left: 6px;">{{ rv.status }}</span>
                  </div>
                  <p class="draft-body muted">{{ rv.body_edited || rv.body_generated }}</p>
                </div>
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
import type { JobDetail, VoiceSummary } from '~/composables/useJobs'
import type { StageLabel } from '~/composables/useJobMedia'
import type { ContentVariant, GenerationRun } from '~/composables/useGeneration'
import { contentTypeLabel } from '~/composables/useGeneration'
import type { ApprovalReadiness } from '~/composables/useContentReview'

const route = useRoute()
const api = useApi()
const media = useJobMedia()
const recorder = useVoiceRecorder()
const voiceUpload = useJobVoice()
const gen = useGeneration()
const review = useContentReview()
const publish = usePublish()
const auth = useAuth()
const { statusLabel } = useJobs()

const jobId = computed(() => String(route.params.id))
const job = ref<JobDetail | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const editTitle = ref('')
const savingMeta = ref(false)
const reordering = ref(false)
const uploadNote = ref('')
const voiceNote = ref('')
const transcriptDraft = ref('')
const savingTranscript = ref(false)
const retranscribing = ref(false)
const forceRerecord = ref(false)
const generateNote = ref('')
const generateError = ref('')
const reviewNote = ref('')
const publishNote = ref('')
const livePublicUrl = ref<string | null>(null)
const draftVariants = ref<ContentVariant[]>([])
const draftWarnings = ref<string[]>([])
const editBodies = ref<Record<string, string>>({})
const savingVariantId = ref<string | null>(null)
const readiness = ref<ApprovalReadiness | null>(null)
const regenInstruction = ref('')
const generationRuns = ref<GenerationRun[]>([])
const showHistory = ref(false)
const expandedRunId = ref<string | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)
let pollTimer: ReturnType<typeof setInterval> | null = null

const canApprove = computed(
  () => auth.permissions.value?.can_approve_and_publish === true,
)

const showReviewWorkspace = computed(() => {
  if (!job.value) return false
  if (draftVariants.value.length > 0) return true
  return ['awaiting_review', 'revision_requested', 'approved', 'published'].includes(job.value.status)
})

function variantStatusLabel(status: string): string {
  const map: Record<string, string> = {
    awaiting_review: 'Needs review',
    approved: 'Approved',
    rejected: 'Rejected',
    superseded: 'Superseded',
    draft: 'Draft',
  }
  return map[status] || status
}

function formatRunDate(iso: string): string {
  try {
    return new Date(iso).toLocaleString()
  } catch {
    return iso
  }
}

function syncEditBodies(variants: ContentVariant[]) {
  const next: Record<string, string> = { ...editBodies.value }
  for (const v of variants) {
    if (next[v.id] === undefined) {
      next[v.id] = (v.body_edited || v.body_generated || '').trim()
    }
  }
  editBodies.value = next
}

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

const showVoiceSection = computed(() => {
  if (!job.value) return false
  if (job.value.photo_counts.after >= 1) return true
  return ['record_voice_summary', 'generate_content'].includes(job.value.next_action.action)
})

const needsRecording = computed(() => {
  if (forceRerecord.value) return true
  const v = job.value?.voice
  if (!v) return true
  if (v.transcription_status === 'failed' && !v.transcript) return true
  return false
})

const recorderStateLabel = computed(() => {
  const s = recorder.state.value
  if (s === 'recording') return 'Recording'
  if (s === 'paused') return 'Paused'
  if (s === 'stopped') return 'Ready to upload'
  if (s === 'unsupported') return 'Unavailable'
  return 'Ready'
})

function applyJob(data: JobDetail) {
  job.value = data
  editTitle.value = data.title
  if (data.voice && !forceRerecord.value) {
    syncTranscriptFromVoice(data.voice)
    maybeStartPolling(data.voice)
  }
}

function syncTranscriptFromVoice(v: VoiceSummary) {
  transcriptDraft.value = (v.transcript_edited || v.transcript_raw || v.transcript || '').trim()
}

function stopPolling() {
  if (pollTimer) {
    clearInterval(pollTimer)
    pollTimer = null
  }
}

function maybeStartPolling(v: VoiceSummary) {
  stopPolling()
  if (v.transcription_status !== 'pending' && v.transcription_status !== 'processing') return
  pollTimer = setInterval(async () => {
    try {
      const voice = (await api.getVoice(jobId.value)) as VoiceSummary
      if (job.value) {
        job.value = { ...job.value, voice }
      }
      if (voice.transcription_status === 'completed' || voice.transcription_status === 'failed') {
        syncTranscriptFromVoice(voice)
        stopPolling()
        await loadJob()
      }
    } catch {
      /* keep polling briefly */
    }
  }, 1500)
}

async function loadDrafts() {
  if (!job.value) return
  const status = job.value.status
  if (!['awaiting_review', 'revision_requested', 'approved', 'generating'].includes(status)) {
    if (
      job.value.next_action.action !== 'review_content' &&
      job.value.next_action.action !== 'ready_to_publish'
    ) {
      draftVariants.value = []
      draftWarnings.value = []
      readiness.value = null
      return
    }
  }
  try {
    const content = await gen.getContent(jobId.value)
    const sorted = (content.variants || []).slice().sort((a, b) => {
      const order = ['primary_social', 'short_caption', 'before_after', 'directory_listing']
      return order.indexOf(a.content_type) - order.indexOf(b.content_type)
    })
    draftVariants.value = sorted
    editBodies.value = {}
    syncEditBodies(sorted)
    const warnings =
      (content.structured_details as { warnings?: string[] } | null)?.warnings || []
    if (!draftWarnings.value.length && Array.isArray(warnings)) {
      draftWarnings.value = warnings
    }
    await loadReadiness()
    await loadHistory()
  } catch {
    /* drafts optional until generated */
  }
}

async function loadReadiness() {
  if (!job.value) return
  try {
    readiness.value = await review.getReadiness(jobId.value)
  } catch {
    readiness.value = null
  }
}

async function loadHistory() {
  if (!job.value) return
  try {
    generationRuns.value = (await api.request(
      `/api/v1/jobs/${jobId.value}/generation-runs`,
    )) as GenerationRun[]
  } catch {
    generationRuns.value = []
  }
}

async function toggleRunDetail(runId: string) {
  if (expandedRunId.value === runId) {
    expandedRunId.value = null
    return
  }
  expandedRunId.value = runId
  const existing = generationRuns.value.find((r) => r.id === runId)
  if (existing && existing.variants?.length) return
  try {
    const full = await gen.getRun(runId)
    generationRuns.value = generationRuns.value.map((r) =>
      r.id === runId ? full : r,
    )
  } catch {
    /* ignore */
  }
}

async function doGenerate() {
  generateError.value = ''
  generateNote.value = ''
  reviewNote.value = ''
  try {
    const result = await gen.generate(jobId.value)
    applyJob(result.job)
    draftVariants.value = result.variants || []
    editBodies.value = {}
    syncEditBodies(draftVariants.value)
    draftWarnings.value = result.warnings || []
    generateNote.value = 'Drafts ready — edit and approve below.'
    await loadReadiness()
    await loadHistory()
  } catch (e: any) {
    generateError.value = e?.message || 'Generation failed'
  }
}

async function doRegenerate() {
  generateError.value = ''
  generateNote.value = ''
  reviewNote.value = ''
  try {
    const payload: { user_instruction?: string } = {}
    if (regenInstruction.value.trim()) {
      payload.user_instruction = regenInstruction.value.trim()
    }
    const result = await gen.regenerate(jobId.value, payload)
    applyJob(result.job)
    draftVariants.value = result.variants || []
    editBodies.value = {}
    syncEditBodies(draftVariants.value)
    draftWarnings.value = result.warnings || []
    generateNote.value = 'New drafts generated — previous versions are in history.'
    regenInstruction.value = ''
    await loadReadiness()
    await loadHistory()
  } catch (e: any) {
    generateError.value = e?.message || 'Regeneration failed'
  }
}

async function saveVariant(v: ContentVariant) {
  savingVariantId.value = v.id
  reviewNote.value = ''
  generateError.value = ''
  try {
    const updated = await review.updateVariant(v.id, {
      body_edited: editBodies.value[v.id] ?? '',
    })
    draftVariants.value = draftVariants.value.map((x) =>
      x.id === v.id ? { ...x, ...updated } : x,
    )
    reviewNote.value = 'Edit saved.'
  } catch (e: any) {
    generateError.value = e?.message || 'Could not save edit'
  } finally {
    savingVariantId.value = null
  }
}

async function approveOne(v: ContentVariant) {
  reviewNote.value = ''
  generateError.value = ''
  try {
    const updated = await review.approveVariant(v.id)
    draftVariants.value = draftVariants.value.map((x) =>
      x.id === v.id ? { ...x, ...updated } : x,
    )
    await loadJob()
    reviewNote.value = `${contentTypeLabel(v.content_type)} approved.`
  } catch (e: any) {
    generateError.value = e?.message || 'Could not approve'
  }
}

async function rejectOne(v: ContentVariant) {
  if (!confirm(`Reject ${contentTypeLabel(v.content_type)}? You can regenerate later.`)) return
  reviewNote.value = ''
  generateError.value = ''
  try {
    const updated = await review.rejectVariant(v.id)
    draftVariants.value = draftVariants.value.map((x) =>
      x.id === v.id ? { ...x, ...updated } : x,
    )
    await loadJob()
    reviewNote.value = `${contentTypeLabel(v.content_type)} rejected.`
  } catch (e: any) {
    generateError.value = e?.message || 'Could not reject'
  }
}

async function doPublish() {
  publishNote.value = ''
  generateError.value = ''
  try {
    const result = await publish.publishJob(jobId.value)
    livePublicUrl.value = result.public_url || result.listing?.public_url || null
    publishNote.value = 'Published — your project is live on the directory.'
    await loadJob()
  } catch (e: any) {
    generateError.value = e?.message || 'Publish failed'
  }
}

async function doUnpublish() {
  if (!confirm('Remove this project from the public directory?')) return
  publishNote.value = ''
  generateError.value = ''
  try {
    await publish.unpublishJob(jobId.value)
    livePublicUrl.value = null
    publishNote.value = 'Unpublished — project is no longer public.'
    await loadJob()
  } catch (e: any) {
    generateError.value = e?.message || 'Unpublish failed'
  }
}

async function doApproveAll() {
  reviewNote.value = ''
  generateError.value = ''
  try {
    const result = await review.approveAll(jobId.value)
    applyJob(result.job)
    draftVariants.value = result.variants || []
    editBodies.value = {}
    syncEditBodies(draftVariants.value)
    readiness.value = result.readiness
    if (result.job.status === 'approved') {
      reviewNote.value = 'All content approved — job is ready to publish.'
    } else {
      reviewNote.value =
        result.readiness.blockers?.join(' ') ||
        'Variants approved, but job still needs requirements.'
    }
  } catch (e: any) {
    generateError.value = e?.message || 'Approve all failed'
  }
}

async function doApproveJob() {
  reviewNote.value = ''
  generateError.value = ''
  try {
    const result = await review.approveJob(jobId.value)
    applyJob(result.job)
    draftVariants.value = result.variants || []
    readiness.value = result.readiness
    reviewNote.value = 'Job approved — ready to publish.'
  } catch (e: any) {
    generateError.value = e?.message || 'Job approve failed'
    await loadReadiness()
  }
}

async function loadJob() {
  loading.value = true
  error.value = null
  try {
    const data = (await api.getJob(jobId.value)) as JobDetail
    applyJob(data)
    await loadDrafts()
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

async function submitRecording() {
  if (!job.value) return
  const file = recorder.asFile()
  if (!file) {
    voiceNote.value = 'No recording to upload.'
    return
  }
  voiceNote.value = ''
  try {
    const result = (await voiceUpload.uploadVoice(job.value.id, file, file.name)) as {
      voice: VoiceSummary
      job: JobDetail
    }
    forceRerecord.value = false
    recorder.discard()
    applyJob(result.job)
    voiceNote.value =
      result.voice.transcription_status === 'completed'
        ? 'Transcript ready — review and edit if needed.'
        : 'Uploaded. Waiting for transcript…'
  } catch (e: any) {
    voiceNote.value = e?.message || 'Upload failed'
  }
}

function startRerecord() {
  forceRerecord.value = true
  voiceNote.value = ''
  recorder.discard()
}

async function saveTranscript() {
  if (!job.value || savingTranscript.value) return
  const text = transcriptDraft.value.trim()
  if (!text) {
    voiceNote.value = 'Transcript cannot be empty.'
    return
  }
  savingTranscript.value = true
  voiceNote.value = ''
  try {
    const result = (await api.updateVoiceTranscript(job.value.id, text)) as {
      voice: VoiceSummary
      job: JobDetail
    }
    applyJob(result.job)
    voiceNote.value = 'Transcript saved.'
  } catch (e: any) {
    voiceNote.value = e?.message || 'Could not save transcript'
  } finally {
    savingTranscript.value = false
  }
}

async function doRetranscribe() {
  if (!job.value || retranscribing.value) return
  retranscribing.value = true
  voiceNote.value = ''
  try {
    const result = (await api.retranscribeVoice(job.value.id)) as {
      voice: VoiceSummary
      job: JobDetail
    }
    forceRerecord.value = false
    applyJob(result.job)
    voiceNote.value = 'New transcript ready.'
  } catch (e: any) {
    voiceNote.value = e?.message || 'Retranscribe failed'
  } finally {
    retranscribing.value = false
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
  if (route.hash === '#voice' || job.value?.next_action.action === 'record_voice_summary') {
    await nextTick()
    document.getElementById('voice')?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
})

onBeforeUnmount(() => {
  stopPolling()
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
.voice-card {
  border-color: #b7d0ea;
}
.recorder {
  margin-top: 4px;
}
.rec-timer {
  display: flex;
  align-items: center;
  font-weight: 700;
  font-size: 22px;
  font-variant-numeric: tabular-nums;
  margin-bottom: 12px;
}
.rec-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e1;
  margin-right: 10px;
  flex-shrink: 0;
}
.rec-dot.live {
  background: #dc2626;
  box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.2);
  animation: pulse 1.2s ease-in-out infinite;
}
@keyframes pulse {
  50% {
    opacity: 0.55;
  }
}
.rec-pause {
  background: #fef3c7;
  color: #92400e;
}
.audio-player {
  width: 100%;
  margin-top: 4px;
}
.transcript-area {
  resize: vertical;
  min-height: 110px;
  line-height: 1.45;
  font-family: inherit;
}
.voice-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.draft-card {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 12px;
  margin-bottom: 10px;
}
.draft-type {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--jp-text-secondary);
  margin-bottom: 4px;
}
.draft-title {
  font-weight: 700;
  font-size: 15px;
  margin-bottom: 6px;
}
.draft-body {
  margin: 0;
  font-size: 14px;
  line-height: 1.45;
  white-space: pre-wrap;
}
.draft-card-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 8px;
  margin-bottom: 4px;
}
.status-pill {
  font-size: 11px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  padding: 2px 8px;
  border-radius: 999px;
  background: #e2e8f0;
  color: #475569;
  white-space: nowrap;
}
.st-awaiting_review {
  background: #fef3c7;
  color: #92400e;
}
.st-approved {
  background: #d1fae5;
  color: #065f46;
}
.st-rejected {
  background: #fee2e2;
  color: #991b1b;
}
.st-superseded {
  background: #f1f5f9;
  color: #64748b;
}
.ready-banner {
  background: #d1fae5;
  border: 1px solid #6ee7b7;
  color: #065f46;
  border-radius: 10px;
  padding: 10px 12px;
  font-size: 13px;
  font-weight: 600;
}
.history-run {
  background: #fff;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 10px;
  margin-bottom: 8px;
}
.history-variant {
  border-top: 1px solid #f1f5f9;
  padding-top: 8px;
  margin-top: 8px;
}
</style>
