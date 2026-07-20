<template>
  <div class="page-body" style="padding-top: 48px;">
    <div class="wordmark" style="font-size: 28px; margin-bottom: 8px;">Job<span>Pulse</span></div>
    <p class="muted" style="margin: 0 0 24px;">Sign in to capture jobs and publish marketing.</p>

    <form class="card" @submit.prevent="submit">
      <label class="field">
        <span>Email</span>
        <input v-model="email" type="email" required autocomplete="email" />
      </label>
      <label class="field">
        <span>Password</span>
        <input v-model="password" type="password" required autocomplete="current-password" />
      </label>
      <p v-if="error" class="error">{{ error }}</p>
      <button class="btn btn-primary btn-block" type="submit" :disabled="loading">
        {{ loading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <p class="muted" style="margin-top: 16px; text-align: center;">
      New here?
      <NuxtLink to="/register">Create an account</NuxtLink>
    </p>
  </div>
</template>

<script setup lang="ts">
const api = useApi()
const auth = useAuth()

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function submit() {
  loading.value = true
  error.value = ''
  try {
    const data = (await api.login({
      email: email.value.trim(),
      password: password.value,
    })) as any
    auth.setSession(data)
    const me = (await api.me()) as any
    auth.permissions.value = me.permissions
    if (me.company && !me.company.onboarding_completed) {
      await navigateTo('/onboarding')
    } else {
      await navigateTo('/')
    }
  } catch (e: any) {
    error.value = e?.message || 'Could not sign in.'
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
.field input {
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
