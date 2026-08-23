<script setup lang="ts">
import { SERVICES } from '~/utils/siteContent'

withDefaults(
  defineProps<{
    sourcePageType?: string
    compact?: boolean
  }>(),
  { sourcePageType: 'contact', compact: false },
)

const submitting = ref(false)
const success = ref(false)
const error = ref<string | null>(null)
const route = useRoute()

const form = reactive({
  name: '',
  email: '',
  phone: '',
  service: String(route.query.service || ''),
  message: '',
})

async function onSubmit() {
  error.value = null
  if (!form.name.trim()) {
    error.value = 'Please enter your name.'
    return
  }
  if (!form.phone.trim() && !form.email.trim()) {
    error.value = 'Add a phone number or email so we can reach you.'
    return
  }
  submitting.value = true
  await new Promise((r) => setTimeout(r, 250))
  submitting.value = false
  success.value = true
}
</script>

<template>
  <form class="estimate-form" :class="{ 'estimate-form--compact': compact }" @submit.prevent="onSubmit">
    <div v-if="success" class="form-success" role="status">
      Thanks — we have your request. A Red Clay estimator will follow up shortly. You can also call us.
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
          <select id="est-service" v-model="form.service">
            <option value="">Select a service</option>
            <option v-for="s in SERVICES" :key="s.service_key" :value="s.service_key">
              {{ s.name }}
            </option>
          </select>
        </div>
      </div>
      <div class="form-field">
        <label for="est-msg">Project details</label>
        <textarea id="est-msg" v-model="form.message" :rows="compact ? 3 : 4" placeholder="House, surfaces, timing" />
      </div>
      <p v-if="error" class="form-error" role="alert">{{ error }}</p>
      <button class="btn btn--primary btn--lg" type="submit" :disabled="submitting">
        {{ submitting ? 'Sending…' : 'Request estimate' }}
      </button>
    </template>
  </form>
</template>

<style scoped>
.estimate-form {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.35rem;
}

.btn:disabled {
  opacity: 0.65;
}
</style>
