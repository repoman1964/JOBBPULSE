<template>
  <div style="display: flex; flex-direction: column; height: 100vh; height: 100dvh;">
    <!-- Nav Bar -->
    <div class="nav-bar">
      <button class="nav-back" @click="navigateTo('/new-job')">←</button>
      <div class="nav-title">Capture</div>
      <button class="nav-action" @click="submitJob" :disabled="submitting">
        {{ submitting ? '...' : 'Submit' }}
      </button>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Progress -->
      <div style="font-size: 12px; color: var(--jp-text-secondary); display: flex; align-items: center; gap: 6px;">
        <div class="progress-steps" style="flex: 1;">
          <div class="step-dot done"></div>
          <div class="step-line done"></div>
          <div class="step-dot active"></div>
          <div class="step-line"></div>
          <div class="step-dot"></div>
          <div class="step-line"></div>
          <div class="step-dot"></div>
        </div>
        <span>Step 2 of 4</span>
      </div>

      <!-- Photos Section -->
      <div class="section-head">Photos</div>

      <div class="capture-area" @click="takePhoto">
        <div class="corner-tl"></div>
        <div class="corner-tr"></div>
        <div class="corner-bl"></div>
        <div class="corner-br"></div>
        <div style="display: flex; flex-direction: column; align-items: center; gap: 8px;">
          <div class="shutter">
            <div class="shutter-inner"></div>
          </div>
          <div class="capture-hint">Tap to capture</div>
        </div>
      </div>

      <!-- Hidden file input -->
      <input
        ref="photoInput"
        type="file"
        accept="image/*"
        capture="environment"
        multiple
        style="display: none;"
        @change="onPhotosSelected"
      >

      <!-- Photo Strip -->
      <div class="photo-strip">
        <div
          v-for="(photo, i) in photos"
          :key="i"
          class="photo-thumb"
        >
          <img :src="photo.preview" :alt="`Photo ${i + 1}`">
          <div
            @click.stop="removePhoto(i)"
            style="position: absolute; top: 2px; right: 2px; width: 16px; height: 16px; border-radius: 50%; background: rgba(0,0,0,0.5); color: white; font-size: 10px; display: flex; align-items: center; justify-content: center; cursor: pointer;"
          >×</div>
        </div>
        <div class="photo-thumb photo-add" @click="addMorePhotos">
          <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
            <path d="M9 3V15M3 9H15" stroke="var(--jp-border)" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
      </div>

      <!-- Voice Recorder -->
      <div class="section-head">Voice note</div>
      <div class="voice-area" @click="toggleRecording">
        <div :class="['rec-btn', { active: recording }]">
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
            <rect x="5" y="2" width="6" height="9" rx="3" :fill="recording ? 'white' : '#E24B4A'"/>
            <path d="M3 8C3 10.76 5.24 13 8 13C10.76 13 13 10.76 13 8" :stroke="recording ? 'white' : '#E24B4A'" stroke-width="1.5" stroke-linecap="round"/>
            <path d="M8 13V15M6 15H10" :stroke="recording ? 'white' : '#E24B4A'" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </div>
        <div class="waveform" ref="waveformEl">
          <span v-if="!recording && !audioBlob" style="font-size: 12px; color: var(--jp-text-secondary);">
            Tap to record voice note
          </span>
          <span v-else-if="!recording && audioBlob" style="font-size: 12px; color: var(--jp-text-secondary);">
            Note recorded ({{ recordedDuration }}s) — tap to re-record
          </span>
          <template v-else>
            <div
              v-for="i in 28"
              :key="i"
              class="wave-bar"
              :style="{ height: waveBars[i - 1] + 'px', background: '#E24B4A', opacity: 0.4 + Math.random() * 0.6 }"
            ></div>
          </template>
        </div>
        <div style="font-size: 11px; color: var(--jp-text-secondary);">{{ timerDisplay }}</div>
      </div>

      <!-- Hint -->
      <div style="background: var(--jp-bg-secondary); border-radius: 10px; padding: 10px 12px; display: flex; align-items: center; gap: 8px;">
        <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
          <circle cx="7" cy="7" r="6" fill="#185FA5" opacity="0.2"/>
          <path d="M7 4V8" stroke="#185FA5" stroke-width="1.5" stroke-linecap="round"/>
          <circle cx="7" cy="10.5" r="0.75" fill="#185FA5"/>
        </svg>
        <span style="font-size: 11px; color: var(--jp-text-secondary);">AI will transcribe your note and generate posts</span>
      </div>

      <button class="btn-primary" @click="submitJob" :disabled="submitting">
        {{ submitting ? 'Submitting...' : 'Submit job →' }}
      </button>
    </div>
  </div>
</template>

<script setup>
const api = useApi()
const photoInput = ref(null)
const waveformEl = ref(null)

// Photo state
const photos = ref([])

// Voice recorder state
const recording = ref(false)
const audioBlob = ref(null)
const recordedDuration = ref(0)
const timerDisplay = ref('0:00')
const waveBars = ref(Array.from({ length: 28 }, () => 4 + Math.random() * 22))
let mediaRecorder = null
let audioChunks = []
let timerInterval = null
let waveInterval = null
let seconds = 0

const takePhoto = () => {
  if (photoInput.value) {
    photoInput.value.click()
  }
}

const addMorePhotos = () => {
  if (photoInput.value) {
    photoInput.value.click()
  }
}

const onPhotosSelected = (e) => {
  const files = Array.from(e.target.files || [])
  for (const file of files) {
    photos.value.push({
      file,
      preview: URL.createObjectURL(file),
    })
  }
  // Reset input so same file can be re-selected
  e.target.value = ''
}

const removePhoto = (index) => {
  URL.revokeObjectURL(photos.value[index].preview)
  photos.value.splice(index, 1)
}

const toggleRecording = async () => {
  if (recording.value) {
    // Stop recording
    if (mediaRecorder && mediaRecorder.state !== 'inactive') {
      mediaRecorder.stop()
    }
    recording.value = false
    clearInterval(timerInterval)
    clearInterval(waveInterval)
    recordedDuration.value = seconds
  } else {
    // Start recording
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      mediaRecorder = new MediaRecorder(stream)
      audioChunks = []

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunks.push(e.data)
      }

      mediaRecorder.onstop = () => {
        audioBlob.value = new Blob(audioChunks, { type: 'audio/webm' })
        stream.getTracks().forEach(t => t.stop())
      }

      mediaRecorder.start()
      recording.value = true
      seconds = 0
      timerDisplay.value = '0:00'

      timerInterval = setInterval(() => {
        seconds++
        const m = Math.floor(seconds / 60)
        const s = seconds % 60
        timerDisplay.value = `${m}:${s < 10 ? '0' : ''}${s}`
      }, 1000)

      waveInterval = setInterval(() => {
        waveBars.value = Array.from({ length: 28 }, () => 4 + Math.random() * 22)
      }, 200)
    } catch (err) {
      console.error('Microphone access denied:', err)
      alert('Please allow microphone access to record a voice note.')
    }
  }
}

const submitting = ref(false)

const submitJob = async () => {
  if (submitting.value) return

  // Get job data from sessionStorage
  const raw = sessionStorage.getItem('jobpulse_new_job')
  if (!raw) {
    alert('Job data not found. Please go back and fill in job details.')
    return
  }

  const jobData = JSON.parse(raw)
  submitting.value = true

  try {
    // Build FormData
    const formData = new FormData()
    formData.append('job_type', jobData.job_type)
    if (jobData.title) formData.append('title', jobData.title)
    if (jobData.customer_name) formData.append('customer_name', jobData.customer_name)
    if (jobData.latitude) formData.append('latitude', String(jobData.latitude))
    if (jobData.longitude) formData.append('longitude', String(jobData.longitude))
    if (jobData.city) formData.append('city', jobData.city)
    if (jobData.state) formData.append('state', jobData.state)
    if (jobData.address) formData.append('address', jobData.address)
    formData.append('platforms', jobData.platforms)

    // Add photos
    for (const photo of photos.value) {
      formData.append('photos', photo.file)
    }

    // Add audio
    if (audioBlob.value) {
      formData.append('audio', audioBlob.value, 'voice_note.webm')
    }

    // Submit
    const result = await api.createJob(formData)

    // Clear sessionStorage
    sessionStorage.removeItem('jobpulse_new_job')

    // Navigate to processing
    navigateTo(`/processing?jobId=${result.id}`)
  } catch (err) {
    console.error('Submit failed:', err)
    alert(`Submit failed: ${err.message}`)
  } finally {
    submitting.value = false
  }
}

// Cleanup on unmount
onUnmounted(() => {
  clearInterval(timerInterval)
  clearInterval(waveInterval)
  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    mediaRecorder.stop()
  }
  photos.value.forEach(p => URL.revokeObjectURL(p.preview))
})
</script>
