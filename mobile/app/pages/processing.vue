<template>
  <div style="display: flex; flex-direction: column; height: 100vh; height: 100dvh;">
    <!-- Nav Bar -->
    <div class="nav-bar">
      <div class="nav-title">Processing</div>
    </div>

    <!-- Processing State -->
    <div class="processing-state">
      <div class="spinner" v-if="!done"></div>
      <div v-else style="width: 40px; height: 40px; border-radius: 50%; background: var(--jp-success-bg); display: flex; align-items: center; justify-content: center; font-size: 18px;">
        ✓
      </div>

      <div style="font-size: 15px; font-weight: 500; color: var(--jp-text-primary); text-align: center;">
        {{ done ? 'Content ready!' : 'Generating your content' }}
      </div>

      <div style="display: flex; flex-direction: column; gap: 10px; width: 100%;">
        <!-- Step 1: Upload -->
        <div class="proc-step">
          <div :class="['proc-icon', step >= 1 ? 'done' : (step === 0 ? 'active' : '')]">
            {{ step >= 1 ? '✓' : '1' }}
          </div>
          <span :style="{ color: step >= 1 ? 'var(--jp-text-primary)' : undefined }">
            {{ step >= 1 ? 'Photos uploaded' : 'Uploading photos...' }}
          </span>
        </div>

        <!-- Step 2: Transcribe -->
        <div class="proc-step">
          <div :class="['proc-icon', step >= 2 ? 'done' : (step === 1 ? 'active' : '')]">
            {{ step >= 2 ? '✓' : '2' }}
          </div>
          <span :style="{ color: step >= 2 ? 'var(--jp-text-primary)' : undefined }">
            {{ step >= 2 ? 'Voice transcribed' : (step === 1 ? 'Transcribing voice...' : 'Transcribe voice') }}
          </span>
        </div>

        <!-- Step 3: AI Writing -->
        <div class="proc-step">
          <div :class="['proc-icon', step >= 3 ? 'done' : (step === 2 ? 'active' : '')]">
            {{ step >= 3 ? '✓' : '3' }}
          </div>
          <span :style="{ color: step >= 3 ? 'var(--jp-text-primary)' : undefined }">
            {{ step >= 3 ? 'Posts generated' : (step === 2 ? 'AI writing posts...' : 'AI write posts') }}
          </span>
        </div>

        <!-- Step 4: Location -->
        <div class="proc-step">
          <div :class="['proc-icon', step >= 4 ? 'done' : (step === 3 ? 'active' : '')]">
            {{ step >= 4 ? '✓' : '4' }}
          </div>
          <span :style="{ color: step >= 4 ? 'var(--jp-text-primary)' : undefined }">
            {{ step >= 4 ? 'Location tags attached' : 'Attach location tags' }}
          </span>
        </div>
      </div>

      <!-- Error -->
      <div v-if="error" style="color: var(--jp-danger); font-size: 12px; text-align: center; padding: 8px;">
        {{ error }}
      </div>

      <button
        v-if="done"
        class="btn-primary"
        style="width: 100%; margin-top: 8px;"
        @click="navigateTo(`/jobs/${jobId}`)"
      >
        Preview drafts →
      </button>

      <button
        v-if="error"
        class="btn-secondary"
        style="width: 100%; margin-top: 8px;"
        @click="retry"
      >
        Retry
      </button>
    </div>
  </div>
</template>

<script setup>
const route = useRoute()
const api = useApi()

const jobId = ref(String(route.query.jobId || ''))
const step = ref(0)
const done = ref(false)
const error = ref('')

const processJob = async () => {
  if (!jobId.value) {
    error.value = 'No job ID provided'
    return
  }

  error.value = ''

  try {
    // Simulate step 1 — photos already uploaded during submit
    step.value = 1
    await new Promise(r => setTimeout(r, 800))

    // Step 2-4: Call generate endpoint (handles transcribe + AI + location)
    step.value = 2
    await new Promise(r => setTimeout(r, 500))

    const result = await api.generateContent(jobId.value)

    step.value = 3
    await new Promise(r => setTimeout(r, 600))

    step.value = 4
    await new Promise(r => setTimeout(r, 400))

    done.value = true
  } catch (err) {
    error.value = err.message || 'Processing failed'
  }
}

const retry = () => {
  step.value = 0
  done.value = false
  processJob()
}

onMounted(() => {
  processJob()
})
</script>
