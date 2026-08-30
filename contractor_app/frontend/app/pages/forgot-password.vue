<script setup lang="ts">
definePageMeta({ layout: 'default' })

const api = useApi()

const email = ref('')
const loading = ref(false)
const error = ref('')
const sent = ref(false)
const resetUrl = ref<string | null>(null)

async function submit() {
  error.value = ''
  if (!email.value.trim()) {
    error.value = 'Enter the email for your account.'
    return
  }
  loading.value = true
  try {
    const result = await api.requestPasswordReset(email.value.trim())
    resetUrl.value = result.resetUrl || null
    sent.value = true
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not send a reset email. Try again.'
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
        <h1 class="page-title">Forgot password</h1>
        <p class="muted">
          <template v-if="sent">
            Check your inbox for a link to choose a new password.
          </template>
          <template v-else>
            We’ll email a reset link if that address has an active JobbPulse account.
          </template>
        </p>
      </div>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>

      <form v-if="!sent" class="card stack" @submit.prevent="submit">
        <div class="field">
          <label for="email">Email</label>
          <input
            id="email"
            v-model="email"
            type="email"
            autocomplete="username"
            placeholder="you@company.com"
          />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Sending…' : 'Send reset link' }}
        </button>
        <NuxtLink class="btn btn-secondary" to="/sign-in">Back to sign in</NuxtLink>
      </form>

      <div v-else class="card stack">
        <p class="muted">
          If an account exists for <strong>{{ email }}</strong>, we sent a reset link.
          It expires in one hour.
        </p>
        <p v-if="resetUrl" class="muted">
          Dev shortcut:
          <a class="link-lime" :href="resetUrl">open the reset page</a>
        </p>
        <button class="btn btn-primary" type="button" :disabled="loading" @click="submit">
          {{ loading ? 'Sending…' : 'Resend reset link' }}
        </button>
        <NuxtLink class="btn btn-secondary" to="/sign-in">Back to sign in</NuxtLink>
      </div>
    </main>
  </div>
</template>

<style scoped>
.sign-in {
  min-height: 100dvh;
}
</style>
