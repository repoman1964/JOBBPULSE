<template>
  <div class="page-body" style="padding-top: 32px;">
    <div class="wordmark" style="font-size: 28px; margin-bottom: 8px;">Job<span>Pulse</span></div>
    <p class="muted" style="margin: 0 0 20px;">Create your company account in under a minute.</p>

    <form class="card" @submit.prevent="submit">
      <label class="field">
        <span>Your name</span>
        <input v-model="fullName" type="text" required autocomplete="name" />
      </label>
      <label class="field">
        <span>Company name</span>
        <input v-model="companyName" type="text" required />
      </label>
      <label class="field">
        <span>Trade</span>
        <select v-model="trade">
          <option value="painting">Painting</option>
          <option value="tree_service">Tree service</option>
          <option value="hardscaping">Hardscaping</option>
          <option value="other">Other</option>
        </select>
      </label>
      <label class="field">
        <span>Email</span>
        <input v-model="email" type="email" required autocomplete="email" />
      </label>
      <label class="field">
        <span>Password (min 8 characters)</span>
        <input v-model="password" type="password" required minlength="8" autocomplete="new-password" />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn btn-primary btn-block" type="submit" :disabled="loading">
        {{ loading ? 'Creating…' : 'Create account' }}
      </button>
    </form>

    <p class="muted" style="margin-top: 16px; text-align: center;">
      Already have an account?
      <NuxtLink to="/login">Sign in</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const auth = useAuth()

const fullName = ref('')
const companyName = ref('')
const trade = ref('painting')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const data = (await api.register({
      email: email.value.trim(),
      password: password.value,
      full_name: fullName.value.trim(),
      company_name: companyName.value.trim(),
      trade: trade.value,
    })) as any
    auth.setSession(data)
    const me = (await api.me()) as any
    auth.permissions.value = me.permissions
    await navigateTo('/onboarding')
  } catch (e: any) {
    error.value = e?.message || 'Could not create account.'
  } finally {
    loading.value = false
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
