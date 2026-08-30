<script setup lang="ts">
definePageMeta({ layout: 'default' })

const api = useApi()
const route = useRoute()
const { setSession } = useAuthSession()

const step = ref<'sign-in' | 'register' | 'check-email'>('sign-in')
const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')
const notice = ref('')
const pendingEmail = ref('')
const registerForm = reactive({
  name: '',
  email: '',
  password: '',
  companyName: '',
  phone: '',
})

function errorCode(e: unknown): string | undefined {
  if (e && typeof e === 'object' && 'code' in e && typeof e.code === 'string') {
    return e.code
  }
  return undefined
}

async function finishSignIn(session: Awaited<ReturnType<typeof api.login>>) {
  await setSession(session)
  const redirect = typeof route.query.redirect === 'string' ? route.query.redirect : '/jobs'
  await navigateTo(redirect)
}

async function signIn() {
  error.value = ''
  notice.value = ''
  if (!email.value.trim() || !password.value) {
    error.value = 'Enter your email and password.'
    return
  }
  loading.value = true
  try {
    const session = await api.login(email.value.trim(), password.value)
    await finishSignIn(session)
  } catch (e) {
    if (errorCode(e) === 'email_not_verified') {
      pendingEmail.value = email.value.trim()
      step.value = 'check-email'
      notice.value = ''
      error.value = e instanceof Error ? e.message : 'Confirm your email before signing in.'
    } else {
      error.value = e instanceof Error ? e.message : 'Could not sign in. Try again.'
    }
  } finally {
    loading.value = false
  }
}

async function createAccount() {
  error.value = ''
  notice.value = ''
  if (
    !registerForm.name.trim() ||
    !registerForm.email.trim() ||
    !registerForm.companyName.trim() ||
    !registerForm.password
  ) {
    error.value = 'Name, email, password, and company are required.'
    return
  }
  if (registerForm.password.length < 8) {
    error.value = 'Use a password with at least 8 characters.'
    return
  }
  loading.value = true
  try {
    await api.register({
      name: registerForm.name.trim(),
      email: registerForm.email.trim(),
      password: registerForm.password,
      companyName: registerForm.companyName.trim(),
      phone: registerForm.phone.trim() || undefined,
    })
    pendingEmail.value = registerForm.email.trim()
    email.value = registerForm.email.trim()
    step.value = 'check-email'
  } catch (e) {
    const code = errorCode(e)
    if (code === 'email_send_failed' || code === 'email_not_configured') {
      pendingEmail.value = registerForm.email.trim()
      email.value = registerForm.email.trim()
      step.value = 'check-email'
      error.value =
        e instanceof Error
          ? e.message
          : 'Account created, but the confirmation email did not send. Tap resend.'
    } else {
      error.value = e instanceof Error ? e.message : 'Could not create that account.'
    }
  } finally {
    loading.value = false
  }
}

async function resend() {
  error.value = ''
  notice.value = ''
  if (!pendingEmail.value) {
    error.value = 'Enter the email you signed up with first.'
    return
  }
  loading.value = true
  try {
    await api.resendVerification(pendingEmail.value)
    notice.value = 'If that account needs confirmation, we sent a new link.'
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not resend that email.'
  } finally {
    loading.value = false
  }
}

async function consumeVerifyQuery() {
  const token = typeof route.query.token === 'string' ? route.query.token : ''
  const verified = route.query.verified
  if (route.query.reset === '1') {
    notice.value = 'Password updated. Sign in with your new password.'
    step.value = 'sign-in'
  }
  if (verified === '1') {
    notice.value = 'Email confirmed. Sign in with your password.'
    step.value = 'sign-in'
    return
  }
  if (verified === '0') {
    error.value = 'That confirmation link is invalid or expired. Request a new one.'
    step.value = 'check-email'
    return
  }
  if (!token) return
  loading.value = true
  try {
    const result = await api.verifyEmail(token)
    email.value = result.email
    pendingEmail.value = result.email
    notice.value = 'Email confirmed. Sign in with your password.'
    step.value = 'sign-in'
    await navigateTo({ path: '/sign-in', query: { verified: '1' } }, { replace: true })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'That confirmation link is not valid.'
    step.value = 'check-email'
  } finally {
    loading.value = false
  }
}

function backToSignIn() {
  error.value = ''
  notice.value = ''
  step.value = 'sign-in'
}

onMounted(() => {
  void consumeVerifyQuery()
})
</script>

<template>
  <div class="sign-in">
    <JpHeader :show-menu="false" />
    <main class="app-main stack-lg">
      <div>
        <h1 class="page-title">{{ step === 'register' ? 'Create account' : 'Sign in' }}</h1>
        <p class="muted">
          <template v-if="step === 'register'">
            We’ll email a confirmation link. After you confirm, sign in with your password.
          </template>
          <template v-else-if="step === 'check-email'">
            Check your inbox to activate the account, then come back here to sign in.
          </template>
          <template v-else>
            Use the email and password you signed up with.
          </template>
        </p>
      </div>

      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <div v-else-if="notice" class="banner" role="status">{{ notice }}</div>

      <form v-if="step === 'sign-in'" class="card stack" @submit.prevent="signIn">
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
        <div class="field">
          <label for="password">Password</label>
          <input
            id="password"
            v-model="password"
            type="password"
            autocomplete="current-password"
          />
          <NuxtLink class="link-lime field-link" to="/forgot-password">Forgot password?</NuxtLink>
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
        <button
          class="btn btn-secondary"
          type="button"
          :disabled="loading"
          @click="step = 'register'"
        >
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
          <label for="reg-password">Password</label>
          <input
            id="reg-password"
            v-model="registerForm.password"
            type="password"
            autocomplete="new-password"
          />
        </div>
        <div class="field">
          <label for="reg-company">Company</label>
          <input
            id="reg-company"
            v-model="registerForm.companyName"
            type="text"
            autocomplete="organization"
          />
        </div>
        <div class="field">
          <label for="reg-phone">Phone (optional)</label>
          <input id="reg-phone" v-model="registerForm.phone" type="tel" autocomplete="tel" />
        </div>
        <button class="btn btn-primary" type="submit" :disabled="loading">
          {{ loading ? 'Creating…' : 'Create account' }}
        </button>
        <button
          class="btn btn-secondary"
          type="button"
          :disabled="loading"
          @click="step = 'sign-in'"
        >
          Sign in instead
        </button>
      </form>

      <div v-else class="card stack">
        <p class="muted">
          We sent a confirmation link to
          <strong>{{ pendingEmail || 'your email' }}</strong>.
        </p>
        <button class="btn btn-primary" type="button" :disabled="loading" @click="resend">
          {{ loading ? 'Sending…' : 'Resend confirmation' }}
        </button>
        <button
          class="btn btn-secondary"
          type="button"
          :disabled="loading"
          @click="backToSignIn"
        >
          Back to sign in
        </button>
      </div>
    </main>
  </div>
</template>

<style scoped>
.sign-in {
  min-height: 100dvh;
}

.field-link {
  align-self: flex-start;
  font-size: 0.9rem;
}
</style>
