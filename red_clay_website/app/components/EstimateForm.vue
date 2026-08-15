<script setup lang="ts">
import { SERVICES } from '~/utils/siteContent'

const props = withDefaults(
  defineProps<{
    sourcePageType?: string
    compact?: boolean
  }>(),
  { sourcePageType: 'contact', compact: false },
)

const api = useJobPulse()
const submitting = ref(false)
const success = ref(false)
const error = ref<string | null>(null)

const route = useRoute()

const form = reactive({
  name: '',
  email: '',
  phone: '',
  service_requested: String(route.query.service || ''),
  project_location: String(route.query.location || ''),
  message: '',
  preferred_contact_method: 'phone',
})

watch(
  () => route.query.service,
  (v) => {
    if (v) form.service_requested = String(v)
  },
)

watch(
  () => route.query.location,
  (v) => {
    if (v) form.project_location = String(v)
  },
)

async function onSubmit() {
  error.value = null
  success.value = false
  if (!form.name.trim()) {
    error.value = 'Please enter your name.'
    return
  }
  if (!form.phone.trim() && !form.email.trim()) {
    error.value = 'Add a phone number or email so we can reach you.'
    return
  }

  submitting.value = true
  try {
    await api.createLead({
      name: form.name.trim(),
      email: form.email.trim() || undefined,
      phone: form.phone.trim() || undefined,
      service_requested: form.service_requested || undefined,
      project_location: form.project_location.trim() || undefined,
      message: form.message.trim() || undefined,
      preferred_contact_method: form.preferred_contact_method,
      source_page_type: props.sourcePageType,
      source_page_url: import.meta.client ? window.location.href : undefined,
    })
    success.value = true
    form.name = ''
    form.email = ''
    form.phone = ''
    form.service_requested = ''
    form.project_location = ''
    form.message = ''
  } catch (e: unknown) {
    // Demo-friendly: still show success path messaging if API rejects offline
    const msg = e instanceof Error ? e.message : 'Could not send right now.'
    error.value = `${msg} You can also call us—we answer the phone.`
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="estimate-form" :class="{ 'estimate-form--compact': compact }" @submit.prevent="onSubmit">
    <div v-if="success" class="form-success" role="status">
      Thanks—we got your request. A Red Clay team member will follow up shortly.
    </div>
    <template v-else>
      <div class="form-row form-row--2">
        <div class="form-field">
          <label for="est-name">Name *</label>
          <input id="est-name" v-model="form.name" type="text" autocomplete="name" required />
        </div>
        <div class="form-field">
          <label for="est-phone">Phone</label>
          <input id="est-phone" v-model="form.phone" type="tel" autocomplete="tel" />
        </div>
      </div>
      <div class="form-row form-row--2">
        <div class="form-field">
          <label for="est-email">Email</label>
          <input id="est-email" v-model="form.email" type="email" autocomplete="email" />
        </div>
        <div class="form-field">
          <label for="est-service">Service</label>
          <select id="est-service" v-model="form.service_requested">
            <option value="">Select a service</option>
            <option v-for="s in SERVICES" :key="s.service_key" :value="s.service_key">
              {{ s.name }}
            </option>
          </select>
        </div>
      </div>
      <div v-if="!compact" class="form-field">
        <label for="est-loc">Project city / neighborhood</label>
        <input id="est-loc" v-model="form.project_location" type="text" placeholder="e.g. Buckhead, Atlanta" />
      </div>
      <div class="form-field">
        <label for="est-msg">Project details</label>
        <textarea
          id="est-msg"
          v-model="form.message"
          :rows="compact ? 3 : 4"
          placeholder="Kitchen size, timeline, cabinet source, etc."
        />
      </div>
      <div class="form-field">
        <label for="est-pref">Preferred contact</label>
        <select id="est-pref" v-model="form.preferred_contact_method">
          <option value="phone">Phone</option>
          <option value="text">Text</option>
          <option value="email">Email</option>
        </select>
      </div>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="btn btn--primary btn--lg" type="submit" :disabled="submitting">
        {{ submitting ? 'Sending…' : 'Request free estimate' }}
      </button>
      <p class="estimate-form__fine muted">No spam. We only use this to respond about your project.</p>
    </template>
  </form>
</template>

<style scoped>
.estimate-form {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow);
}

.estimate-form--compact {
  padding: 1rem;
}

.estimate-form__fine {
  margin: 0.75rem 0 0;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}
</style>
