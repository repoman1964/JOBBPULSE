<script setup lang="ts">
definePageMeta({ layout: 'default' })

const api = useApi()
const route = useRoute()
const { setSession } = useAuthSession()

const step = ref<'identifier' | 'register' | 'code'>('identifier')
const identifier = ref('mike@johnsonoutdoor.example')
const code = ref('')
const challengeId = ref('')
const devCode = ref<string | null>(null)
const loading = ref(false)
const error = ref('')
const registerForm = reactive({
  name: '',
  email: '',
  companyName: '',
  phone: '',
})

async function requestCode() {
  error.value = ''
  if (!identifier.value.trim()) {
    error.value = 'Enter your email or phone number.'
    return
  }
  loading.value = true
  try {
    const res = await api.requestChallenge(identifier.value.trim())
    challengeId.value = res.challengeId
    devCode.value = res.devCode || null
    if (res.devCode) code.value = res.devCode
    step.value = 'code'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not send a code. Try again.'
  } finally {
    loading.value = false
  }
}

async function createAccount() {
  error.value = ''
  if (!registerForm.name.trim() || !registerForm.email.trim() || !registerForm.companyName.trim()) {
    error.value = 'Name, email, and company are required.'
    return
  }
  loading.value = true
  try {
    await api.register({
      name: registerForm.name.trim(),
      email: registerForm.email.trim(),
      companyName: registerForm.companyName.trim(),
      phone: registerForm.phone.trim() || undefined,
    })
    identifier.value = registerForm.email.trim()
    const res = await api.requestChallenge(identifier.value)
    challengeId.value = res.challengeId
    devCode.value = res.devCode || null
    if (res.devCode) code.value = res.devCode
    step.value = 'code'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not create that account.'
  } finally {
    loading.value = false
  }
}

async function verify() {
  error.value = ''
  if (!code.value.trim()) {
    error.value = 'Enter the one-time code.'
    return
  }
  loading.value = true
  try {
    const session = await api.verifyChallenge(challengeId.value, code.value.trim())
    await setSession(session)
    const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/jobs'
    await navigateTo(redirect)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not verify that code.'
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
        <h1 class="page-title">Sign in</h1>
        <p class="muted">
          Enter your email or phone. JobbPulse sends a one-time code — no password needed.
        </p>
      </div>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>

      <form v-if="step === 'identifier'" class="card stack" @submit.prevent="requestCode">
        <div class="field">
          <label for="identifier">Email or phone</label>
          <input
            id="identifier"
            v-model="identifier"
            type="text"
            autocomplete="username"
            inputmode="email"
            placeholder="you@company.com"
          />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Sending…' : 'Send code' }}
        </button>
        <button class="btn btn-secondary" type="button" :disabled="loading" @click="step = 'register'">
          Create account
        </button>
      </form>

      <form v-else-if="step === 'register'" class="card stack" @submit.prevent="createAccount">
        <div class="field">
          <label for="reg-name">Your name</label>
          <input id="reg-name" v-model="registerForm.name" type="text" autocomplete="name" />
        </div>
        <div class="field">
          <label for="reg-email">Email</label>
          <input id="reg-email" v-model="registerForm.email" type="email" autocomplete="email" />
        </div>
        <div class="field">
          <label for="reg-company">Company</label>
          <input id="reg-company" v-model="registerForm.companyName" type="text" autocomplete="organization" />
        </div>
        <div class="field">
          <label for="reg-phone">Phone (optional)</label>
          <input id="reg-phone" v-model="registerForm.phone" type="tel" autocomplete="tel" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Creating…' : 'Create account' }}
        </button>
        <button class="btn btn-secondary" type="button" :disabled="loading" @click="step = 'identifier'">
          Sign in instead
        </button>
      </form>

      <form v-else class="card stack" @submit.prevent="verify">
        <div class="field">
          <label for="code">One-time code</label>
          <input
            id="code"
            v-model="code"
            type="text"
            inputmode="numeric"
            autocomplete="one-time-code"
            placeholder="6-digit code"
          />
        </div>
        <p v-if="devCode" class="helper-text">
          Mock mode code: <strong>{{ devCode }}</strong> (also logged in the browser console)
        </p>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Checking…' : 'Sign in' }}
        </button>
        <button class="btn btn-secondary" type="button" :disabled="loading" @click="step = 'identifier'">
          Use a different email
        </button>
      </form>
    </main>
  </div>
</template>

<style scoped>
.sign-in {
  min-height: 100dvh;
}
</style>
