<template>
  <div style="display: flex; flex-direction: column; height: 100vh; height: 100dvh;">
    <!-- Nav Bar -->
    <div class="nav-bar">
      <button class="nav-back" @click="navigateTo('/')">←</button>
      <div class="nav-title">New job</div>
      <button class="nav-action" @click="goToCapture" :disabled="!form.job_type">Next</button>
    </div>

    <!-- Form -->
    <div class="content">
      <div class="form-field">
        <div class="field-label">Job type</div>
        <select class="field-input field-select" v-model="form.job_type">
          <option value="">Select job type...</option>
          <option v-for="t in jobTypes" :key="t" :value="t">{{ t }}</option>
        </select>
      </div>

      <div class="form-field">
        <div class="field-label">Job title (optional)</div>
        <input class="field-input" type="text" v-model="form.title" placeholder="e.g. Ductless mini-split install">
      </div>

      <div class="form-field">
        <div class="field-label">Customer name</div>
        <input class="field-input" type="text" v-model="form.customer_name" placeholder="e.g. Johnson Residence">
      </div>

      <div class="divider"></div>

      <!-- GPS Location -->
      <div class="field-label">Location</div>
      <div style="display: flex; align-items: center; justify-content: space-between; background: var(--jp-bg-secondary); border-radius: 10px; padding: 10px 12px;">
        <div v-if="locData.location">
          <div style="font-size: 13px; color: var(--jp-text-primary); font-weight: 500;">
            {{ locData.location.address || 'Address unavailable' }}{{ locData.location.city ? `, ${locData.location.city}` : '' }}
          </div>
          <div style="font-size: 11px; color: var(--jp-text-secondary);">
            GPS · {{ locData.location?.latitude?.toFixed(4) }}° N, {{ Math.abs(locData.location?.longitude || 0).toFixed(4) }}° W
          </div>
        </div>
        <div v-else-if="locData.loading">
          <div style="font-size: 13px; color: var(--jp-text-secondary);">Getting location...</div>
        </div>
        <div v-else>
          <div style="font-size: 13px; color: var(--jp-text-secondary);">Location unavailable</div>
          <div style="font-size: 11px; color: var(--jp-text-secondary);" v-if="locData.error">{{ locData.error }}</div>
        </div>

        <div class="gps-pill" v-if="locData.location">
          <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
            <path d="M6 1C3.79 1 2 2.79 2 5C2 8 6 11 6 11C6 11 10 8 10 5C10 2.79 8.21 1 6 1Z" fill="#185FA5"/>
            <circle cx="6" cy="5" r="1.5" fill="white"/>
          </svg>
          GPS on
        </div>
        <button v-else class="pill" @click="getLocation" style="flex-shrink: 0;">
          {{ locData.loading ? '...' : 'Enable GPS' }}
        </button>
      </div>

      <div class="divider"></div>

      <!-- Publish To -->
      <div class="field-label" style="margin-bottom: 6px;">Publish to</div>
      <div class="pill-row">
        <button
          v-for="p in availablePlatforms"
          :key="p.id"
          :class="['pill', { on: form.platforms.includes(p.id) }]"
          @click="togglePlatform(p.id)"
        >
          {{ p.label }}
        </button>
      </div>

      <div class="divider"></div>

      <button class="btn-primary" @click="goToCapture" :disabled="!form.job_type">
        Continue to capture →
      </button>
    </div>
  </div>
</template>

<script setup>
const locData = useLocation()

const jobTypes = [
  'HVAC Installation',
  'Roof Repair',
  'Plumbing',
  'Electrical',
  'Landscaping',
  'Painting',
  'Flooring',
  'Cleaning',
  'General Handyman',
  'Other',
]

const availablePlatforms = [
  { id: 'facebook', label: 'Facebook' },
  { id: 'gbp', label: 'Google Business' },
  { id: 'blog', label: 'Blog' },
]

const form = reactive({
  job_type: '',
  title: '',
  customer_name: '',
  platforms: ['facebook', 'gbp', 'blog'],
})

const togglePlatform = (id) => {
  const idx = form.platforms.indexOf(id)
  if (idx >= 0) {
    form.platforms.splice(idx, 1)
  } else {
    form.platforms.push(id)
  }
}

const getLocation = () => {
  locData.getCurrentLocation()
}

// Auto-fetch location on mount
onMounted(() => {
  locData.getCurrentLocation()
})

const goToCapture = () => {
  // Store form data in sessionStorage for the capture page
  const jobData = {
    ...form,
    platforms: JSON.stringify(form.platforms),
    latitude: locData.location.value?.latitude || null,
    longitude: locData.location.value?.longitude || null,
    city: locData.location.value?.city || '',
    state: locData.location.value?.state || '',
    address: locData.location.value?.address || '',
  }
  sessionStorage.setItem('jobpulse_new_job', JSON.stringify(jobData))
  navigateTo('/capture')
}
</script>
