<script setup lang="ts">
const demo = useDemoProjects()
const email = ref(demo.emailCookie.value || '')
const message = ref('')
const error = ref('')

useSeoMeta({
  title: 'See your project | Red Clay',
  description: 'Enter the email from the contractor app to see your generated job on this site.',
})

async function onSubmit() {
  error.value = ''
  message.value = ''
  const result = await demo.identify(email.value)
  if (!result.ok) {
    error.value = result.message
    return
  }
  message.value = result.message
  if (result.count > 0) {
    await navigateTo('/#recent-work')
  }
}

function onClear() {
  demo.clearEmail()
  email.value = ''
  message.value = 'Cleared. Dummy projects remain on the site.'
  error.value = ''
}
</script>

<template>
  <div>
    <section class="page-hero">
      <div class="container">
        <p class="section__eyebrow">Your project</p>
        <h1 class="page-hero__title">See your project</h1>
        <p class="section__lead">
          Use the same email you used in the contractor app. We will show that job on the homepage and here.
        </p>
      </div>
    </section>
    <section class="section">
      <div class="container" style="max-width: 32rem">
        <form class="estimate-form" @submit.prevent="onSubmit">
          <div class="form-field">
            <label for="demo-email">Email</label>
            <input id="demo-email" v-model="email" type="email" autocomplete="email" required />
          </div>
          <p v-if="error" class="form-error" role="alert">{{ error }}</p>
          <p v-else-if="message" class="form-success" role="status">{{ message }}</p>
          <button class="btn btn--primary" type="submit">Continue</button>
          <button class="btn btn--secondary" type="button" style="margin-left: 0.5rem" @click="onClear">
            Clear email
          </button>
        </form>
        <p class="muted" style="margin-top: 1.5rem">
          <NuxtLink to="/work">Browse work</NuxtLink>
        </p>
      </div>
    </section>
  </div>
</template>
