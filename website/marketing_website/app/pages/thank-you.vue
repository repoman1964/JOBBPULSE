<script setup lang="ts">
import { readCheckout } from '~/utils/checkout'

definePageMeta({
  layout: 'checkout',
})

const config = useRuntimeConfig()
const appUrl = config.public.appUrl as string
const email = config.public.contactEmail as string
const founderVideo = (config.public.thankYouVideoUrl as string) || (config.public.vslUrl as string)
const founderPoster =
  (config.public.thankYouVideoPoster as string) || (config.public.vslPoster as string)

const buyerEmail = ref('')

onMounted(() => {
  buyerEmail.value = readCheckout()?.email || ''
})

const steps = [
  {
    title: 'Watch the welcome from the founder',
    body: 'A short video on what happens next and how to get your first finished job into JobbPulse.',
  },
  {
    title: 'Check your email',
    body: 'Account setup and your receipt go to the address you used at checkout. Check spam if you don’t see it.',
  },
  {
    title: 'Sign in to the Contractor App',
    body: 'Use the setup link in that email, or open the app and sign in with the same address.',
  },
  {
    title: 'Connect the accounts you want to publish to',
    body: 'Link the social profiles JobbPulse should post to. You still approve everything before it goes live.',
  },
  {
    title: 'Submit your first finished job',
    body: 'Add the photos and talk for about 30 seconds. That’s the whole capture.',
  },
  {
    title: 'Approve the first content package',
    body: 'Once you approve it, we publish within 48 hours to your Facebook Page, Instagram, Google Business Profile, 3–5 local homeowners groups, your website (carousel and job page), and the JobbPulse directory.',
  },
] as const

useSeoMeta({
  title: 'Thank you | JobbPulse',
  description:
    'You’re in. Watch a short welcome from the founder and follow the next steps to set up JobbPulse.',
})
</script>

<template>
  <section class="thanks">
    <div class="container thanks-wrap">
      <div class="thanks-intro">
        <p class="eyebrow">You’re in</p>
        <h1>Thanks for getting JobbPulse. <span>Here’s how to start.</span></h1>
        <p class="lead">
          Watch this short welcome from the founder, then follow the steps below.
        </p>
        <p v-if="buyerEmail" class="thanks-email">
          We’ll send account setup to <strong>{{ buyerEmail }}</strong>.
        </p>
      </div>

      <SalesVideo
        :src="founderVideo"
        :poster="founderPoster"
        title="Welcome from the JobbPulse founder"
      />

      <div class="thanks-steps">
        <p class="eyebrow">Next steps</p>
        <h2>Get your first job into JobbPulse.</h2>
        <ol class="thanks-list">
          <li v-for="(step, index) in steps" :key="step.title">
            <span class="step-num">{{ index + 1 }}</span>
            <div>
              <h3>{{ step.title }}</h3>
              <p class="muted">{{ step.body }}</p>
            </div>
          </li>
        </ol>
      </div>

      <div class="thanks-actions">
        <a class="btn btn-buy" :href="appUrl">Open the Contractor App</a>
      </div>
      <p class="thanks-note">
        Questions? Write
        <a :href="`mailto:${email}`">{{ email }}</a>.
      </p>
    </div>
  </section>
</template>
