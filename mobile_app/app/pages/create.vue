<template>
  <div>
    <header class="top-bar">
      <NuxtLink to="/" class="muted">← Back</NuxtLink>
      <div style="font-weight: 600;">Create Job</div>
      <span style="width: 48px;" />
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <h1 style="margin: 0 0 6px; font-size: 18px;">Name this job</h1>
        <p class="muted" style="margin: 0;">
          Label it so you can find it later. After photos (and a voice summary) finish the job —
          before photos are optional if you already started work.
        </p>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <label class="field-label">Job name <span class="req">*</span></label>
        <input
          v-model="title"
          class="field-input"
          type="text"
          placeholder="e.g. Johnson / Oak St"
          :disabled="saving"
          maxlength="200"
          autocomplete="off"
        />
        <p class="privacy-note">
          Only you see this name in the app. It is never shared in marketing, AI posts, or the public directory.
        </p>

        <label class="field-label" style="margin-top: 14px;">Service type (optional)</label>
        <select v-model="serviceKey" class="field-input" :disabled="saving">
          <option value="">Use company default</option>
          <option v-for="s in serviceOptions" :key="s.key" :value="s.key">{{ s.label }}</option>
        </select>

        <p v-if="geoHint" class="muted" style="margin: 12px 0 0; font-size: 12px;">
          {{ geoHint }}
        </p>

        <p v-if="error" class="error-text">{{ error }}</p>

        <button
          class="btn btn-primary btn-block"
          type="button"
          style="margin-top: 18px;"
          :disabled="saving || !title.trim()"
          @click="createAndOpen('before')"
        >
          {{ saving ? 'Creating…' : 'Create & add before photos' }}
        </button>
        <button
          class="btn btn-block"
          type="button"
          style="margin-top: 10px; background: #e8eef5; color: var(--jp-primary);"
          :disabled="saving || !title.trim()"
          @click="createAndOpen('after')"
        >
          {{ saving ? 'Creating…' : 'Skip befores — go to after photos' }}
        </button>
        <p class="muted" style="margin: 10px 0 0; font-size: 12px;">
          Before = optional. After + voice = required to complete the job.
        </p>
      </div>

      <p class="muted" style="text-align: center; font-size: 13px;">
        We may use a general area (city) for local marketing later — never your customer’s street address.
        Jobs are saved on the server so you can leave and come back.
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { createJob } = useJobs()
const geo = useLocation()

const title = ref('')
const serviceKey = ref('')
const saving = ref(false)
const error = ref<string | null>(null)
const geoHint = ref('Detecting general area…')

const serviceOptions = [
  { key: 'interior_painting', label: 'Interior painting' },
  { key: 'exterior_painting', label: 'Exterior painting' },
  { key: 'cabinet_painting', label: 'Cabinet painting' },
  { key: 'roofing', label: 'Roofing' },
  { key: 'hardscaping', label: 'Hardscaping' },
  { key: 'landscaping', label: 'Landscaping' },
  { key: 'flooring', label: 'Flooring' },
]

onMounted(async () => {
  const loc = await geo.captureCoarseLocation()
  if (loc?.location_display || loc?.city) {
    geoHint.value = `General area: ${loc.location_display || loc.city}${loc.state ? `, ${loc.state}` : ''} (not a street address)`
  } else {
    geoHint.value = 'General area not set — you can still create the job.'
  }
})

async function createAndOpen(stage: 'before' | 'after' = 'before') {
  if (saving.value) return
  const name = title.value.trim()
  if (!name) {
    error.value = 'Job name is required so you can find this job later.'
    return
  }
  saving.value = true
  error.value = null
  try {
    const payload: Record<string, unknown> = { title: name }
    if (serviceKey.value) payload.service_key = serviceKey.value
    const loc = geo.coarse.value
    if (loc?.city) payload.city = loc.city
    if (loc?.state) payload.state = loc.state
    if (loc?.location_display) payload.location_display = loc.location_display
    const job = await createJob(payload)
    await navigateTo(`/jobs/${job.id}?stage=${stage}`)
  } catch (e: any) {
    error.value = e?.message || 'Could not create job'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.top-bar {
  padding: 12px 16px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--jp-surface);
  border-bottom: 1px solid var(--jp-border);
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
  line-height: 1.4;
}
.error-text {
  color: var(--jp-danger);
  font-size: 14px;
  margin: 12px 0 0;
}
</style>
