<template>
  <div>
    <header style="padding: 16px; background: var(--jp-surface); border-bottom: 1px solid var(--jp-border);">
      <div class="wordmark">Job<span>Pulse</span></div>
      <div class="muted">Onboarding · step {{ step }} of 3</div>
    </header>

    <div class="page-body">
      <div v-if="step === 1" class="card">
        <h1 style="margin: 0 0 8px; font-size: 18px;">Company basics</h1>
        <p class="muted" style="margin: 0 0 16px;">Confirm how customers should reach you.</p>
        <label class="field">
          <span>Phone</span>
          <input v-model="phone" type="tel" placeholder="(555) 555-0100" />
        </label>
        <label class="field">
          <span>Website</span>
          <input v-model="website" type="url" placeholder="https://" />
        </label>
        <label class="field">
          <span>Preferred tone</span>
          <select v-model="tone">
            <option value="friendly_local">Friendly and local</option>
            <option value="straightforward">Straightforward and professional</option>
            <option value="expert_educational">Expert and educational</option>
            <option value="rugged_direct">Rugged and direct</option>
            <option value="premium_polished">Premium and polished</option>
          </select>
        </label>
        <button class="btn btn-primary btn-block" type="button" @click="step = 2">Continue</button>
      </div>

      <div v-else-if="step === 2" class="card">
        <h1 style="margin: 0 0 8px; font-size: 18px;">Services</h1>
        <p class="muted" style="margin: 0 0 16px;">Add at least one service you offer.</p>
        <label class="field">
          <span>Service name</span>
          <input v-model="serviceName" type="text" placeholder="Interior painting" />
        </label>
        <button class="btn btn-primary btn-block" type="button" :disabled="saving" @click="saveServiceAndContinue">
          {{ saving ? 'Saving…' : 'Continue' }}
        </button>
        <button class="btn btn-block" type="button" style="margin-top: 8px; background: #eef2f6;" @click="step = 3">
          Skip for now
        </button>
      </div>

      <div v-else class="card">
        <h1 style="margin: 0 0 8px; font-size: 18px;">Service area</h1>
        <p class="muted" style="margin: 0 0 16px;">Where do you work? City-level is enough.</p>
        <label class="field">
          <span>City / area</span>
          <input v-model="areaName" type="text" placeholder="Austin, TX" />
        </label>
        <p v-if="error" class="error">{{ error }}</p>
        <button class="btn btn-primary btn-block" type="button" :disabled="saving" @click="finish">
          {{ saving ? 'Finishing…' : 'Finish setup' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const auth = useAuth()

const step = ref(1)
const phone = ref('')
const website = ref('')
const tone = ref('friendly_local')
const serviceName = ref('')
const areaName = ref('')
const saving = ref(false)
const error = ref('')

async function saveServiceAndContinue() {
  if (!serviceName.value.trim()) {
    step.value = 3
    return
  }
  saving.value = true
  error.value = ''
  try {
    const key = serviceName.value.trim().toLowerCase().replace(/\s+/g, '_')
    await api.createService({
      service_key: key,
      display_name: serviceName.value.trim(),
    })
    step.value = 3
  } catch (e: any) {
    error.value = e?.message || 'Could not save service.'
  } finally {
    saving.value = false
  }
}

async function finish() {
  saving.value = true
  error.value = ''
  try {
    if (areaName.value.trim()) {
      await api.createServiceArea({
        display_name: areaName.value.trim(),
        is_primary: true,
      })
    }
    const company = (await api.updateCompany({
      phone: phone.value.trim() || null,
      website_url: website.value.trim() || null,
      default_tone: tone.value,
      default_call_to_action: 'Request a free estimate',
      onboarding_completed: true,
    })) as any
    auth.company.value = {
      id: company.id,
      name: company.name,
      slug: company.slug,
      trade: company.trade,
      onboarding_completed: company.onboarding_completed,
    }
    await navigateTo('/')
  } catch (e: any) {
    error.value = e?.message || 'Could not finish onboarding.'
  } finally {
    saving.value = false
  }
}
</script>

<style scoped>
.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
  margin-bottom: 12px;
  font-size: 13px;
  color: var(--jp-text-secondary);
}
.field input,
.field select {
  border: 1px solid var(--jp-border);
  border-radius: 10px;
  padding: 12px;
  font-size: 16px;
  color: var(--jp-text);
  background: #fff;
}
.error {
  color: var(--jp-danger);
  font-size: 13px;
  margin: 0 0 12px;
}
</style>
