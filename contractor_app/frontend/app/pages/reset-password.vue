<script setup lang="ts">
definePageMeta({ layout: 'default' })

const api = useApi()
const route = useRoute()

const token = computed(() => (typeof route.query.token === 'string' ? route.query.token : ''))
const password = ref('')
const confirm = ref('')
const loading = ref(false)
const error = ref('')
const done = ref(false)
const email = ref('')

async function submit() {
  error.value = ''
  if (!token.value) {
    error.value = 'That reset link is missing or invalid. Request a new one.'
    return
  }
  if (password.value.length < 8) {
    error.value = 'Use a password with at least 8 characters.'
    return
  }
  if (password.value !== confirm.value) {
    error.value = 'Those passwords do not match.'
    return
  }
  loading.value = true
  try {
    const result = await api.resetPassword(token.value, password.value)
    email.value = result.email
    done.value = true
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not update that password. Request a new link.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="sign-in">
    <JpHeader :show-menu="false" />
    <main class="app-main stack-lg">
      <div>
        <h1 class="page-title">{{ done ? 'Password updated' : 'Choose a new password' }}</h1>
        <p class="muted">
          <template v-if="done">
            Sign in with your new password for {{ email }}.
          </template>
          <template v-else-if="!token">
            This reset link is missing or invalid.
          </template>
          <template v-else>
            Pick a password with at least 8 characters.
          </template>
        </p>
      </div>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>

      <form v-if="!done && token" class="card stack" @submit.prevent="submit">
        <div class="field">
          <label for="password">New password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="new-password"
          />
        </div>
        <div class="field">
          <label for="confirm">Confirm password</label>
          <input
            id="confirm"
            v-model="confirm"
            type="password"
            autocomplete="new-password"
          />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Saving…' : 'Update password' }}
        </button>
        <NuxtLink class="btn btn-secondary" to="/forgot-password">Request a new link</NuxtLink>
      </form>

      <div v-else class="card stack">
        <NuxtLink class="btn btn-primary" to="/sign-in?reset=1">Sign in</NuxtLink>
        <NuxtLink v-if="!done" class="btn btn-secondary" to="/forgot-password">
          Request a new link
        </NuxtLink>
      </div>
    </main>
  </div>
</template>

<style scoped>
.sign-in {
  min-height: 100dvh;
}
</style>
