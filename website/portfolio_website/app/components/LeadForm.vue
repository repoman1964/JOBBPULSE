<script setup lang="ts">
const props = defineProps<{
  contractorSlug: string
  projectSlug?: string
  serviceRequested?: string
  projectLocation?: string
  sourcePageType?: string
  headline?: string
}>()

const api = usePublicApi()
const route = useRoute()

const name = ref('')
const email = ref('')
const phone = ref('')
const message = ref('')
const preferred = ref('phone')
const projectLocation = ref(props.projectLocation || '')
const serviceRequested = ref(props.serviceRequested || '')
const submitting = ref(false)
const error = ref('')
const success = ref('')

async function submit() {
  error.value = ''
  success.value = ''
  if (!name.value.trim()) {
    error.value = 'Please enter your name.'
    return
  }
  if (!email.value.trim() && !phone.value.trim()) {
    error.value = 'Provide an email or phone number.'
    return
  }
  submitting.value = true
  try {
    const res = await api.createLead({
      contractor_slug: props.contractorSlug,
      name: name.value.trim(),
      email: email.value.trim() || undefined,
      phone: phone.value.trim() || undefined,
      message: message.value.trim() || undefined,
      project_slug: props.projectSlug,
      project_location: projectLocation.value.trim() || undefined,
      service_requested: serviceRequested.value.trim() || undefined,
      preferred_contact_method: preferred.value,
      source_page_type: props.sourcePageType || 'unknown',
      source_page_url: route.fullPath,
    })
    success.value = res.message || 'Thanks — your message was received.'
    name.value = ''
    email.value = ''
    phone.value = ''
    message.value = ''
  } catch (e: any) {
    error.value =
      e?.data?.error?.message ||
      e?.data?.message ||
      e?.message ||
      'Could not send your request. Please try again.'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <form class="lead-form panel" @submit.prevent="submit">
    <h3>{{ headline || 'Interested in a project like this?' }}</h3>
    <p class="muted">Request an estimate from this contractor. Your inquiry is sent directly to them.</p>

    <label for="lead-name">Name</label>
    <input id="lead-name" v-model="name" type="text" autocomplete="name" required />

    <label for="lead-phone">Phone</label>
    <input id="lead-phone" v-model="phone" type="tel" autocomplete="tel" />

    <label for="lead-email">Email</label>
    <input id="lead-email" v-model="email" type="email" autocomplete="email" />

    <label for="lead-location">Project location</label>
    <input id="lead-location" v-model="projectLocation" type="text" placeholder="City or neighborhood" />

    <label for="lead-service">Service needed</label>
    <input id="lead-service" v-model="serviceRequested" type="text" />

    <label for="lead-message">Short project description</label>
    <textarea id="lead-message" v-model="message" />

    <label for="lead-preferred">Preferred contact method</label>
    <select id="lead-preferred" v-model="preferred">
      <option value="phone">Phone</option>
      <option value="email">Email</option>
      <option value="either">Either</option>
    </select>

    <p v-if="error" class="error">{{ error }}</p>
    <p v-if="success" class="success">{{ success }}</p>

    <div style="margin-top: 0.85rem">
      <button class="btn btn-primary btn-block" type="submit" :disabled="submitting">
        {{ submitting ? 'Sending…' : 'Request estimate' }}
      </button>
    </div>
  </form>
</template>
