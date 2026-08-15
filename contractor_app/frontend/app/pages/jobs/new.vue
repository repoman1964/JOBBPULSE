<script setup lang="ts">
const api = useApi()

const form = reactive({
  name: '',
  serviceType: '',
  city: '',
  region: '',
  locationText: '',
  internalNote: '',
  assignedCrewMember: '',
})

const loading = ref(false)
const error = ref('')
const fieldErrors = ref<Record<string, string>>({})

function validate() {
  const errs: Record<string, string> = {}
  if (!form.name.trim()) errs.name = 'Job name is required.'
  if (!form.serviceType.trim()) errs.serviceType = 'Service type is required.'
  if (!form.city.trim()) errs.city = 'City or service location is required.'
  fieldErrors.value = errs
  return !Object.keys(errs).length
}

async function create() {
  error.value = ''
  if (!validate()) return
  loading.value = true
  try {
    const job = await api.createJob({ ...form })
    await navigateTo(`/jobs/${job.id}`)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not create job.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div>
    <JpHeader show-back back-to="/jobs" />
    <main class="app-main">
      <h1 class="page-title">New job</h1>
      <p class="muted">Create a job in under a minute, then start adding photos.</p>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>

      <form class="card stack" style="margin-top: 16px" @submit.prevent="create">
        <div class="field">
          <label for="name">Job name or customer</label>
          <input id="name" v-model="form.name" type="text" autocomplete="off" />
          <span v-if="fieldErrors.name" class="field-error">{{ fieldErrors.name }}</span>
        </div>
        <div class="field">
          <label for="serviceType">Service type</label>
          <input id="serviceType" v-model="form.serviceType" type="text" placeholder="Deck rebuild, painting…" />
          <span v-if="fieldErrors.serviceType" class="field-error">{{ fieldErrors.serviceType }}</span>
        </div>
        <div class="field">
          <label for="city">City</label>
          <input id="city" v-model="form.city" type="text" />
          <span v-if="fieldErrors.city" class="field-error">{{ fieldErrors.city }}</span>
        </div>
        <div class="field">
          <label for="region">State / region (optional)</label>
          <input id="region" v-model="form.region" type="text" placeholder="GA" />
        </div>
        <div class="field">
          <label for="note">Internal note (optional)</label>
          <textarea id="note" v-model="form.internalNote" rows="3" />
        </div>
        <div class="field">
          <label for="crew">Assigned crew (optional)</label>
          <input id="crew" v-model="form.assignedCrewMember" type="text" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Creating…' : 'Create job' }}
        </button>
      </form>
    </main>
  </div>
</template>
