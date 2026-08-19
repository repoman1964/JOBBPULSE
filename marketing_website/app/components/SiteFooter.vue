<script setup lang="ts">
const config = useRuntimeConfig()
const appUrl = config.public.appUrl as string
const email = config.public.contactEmail as string
const year = new Date().getFullYear()
const { show } = useAskModal()
</script>

<template>
  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <p class="brand-name footer-brand">Jobb<span>Pulse</span></p>
        <p class="muted">Marketing everywhere from your finished jobs.</p>
      </div>
      <div>
        <p class="footer-label">Product</p>
        <a href="#how-it-works">How it works</a>
        <a href="#what-you-get">What you get</a>
        <a href="#lead-desk">Lead Desk</a>
        <button type="button" class="footer-ask" @click="show">Ask us about JobbPulse</button>
        <a :href="appUrl">Sign in</a>
      </div>
      <div>
        <p class="footer-label">Company</p>
        <a :href="`mailto:${email}`">{{ email }}</a>
        <NuxtLink to="/privacy">Privacy Policy</NuxtLink>
        <NuxtLink to="/terms">Terms of Service</NuxtLink>
        <NuxtLink to="/refund">Refund Policy</NuxtLink>
      </div>
    </div>
    <div class="container footer-bottom">
      <p>© {{ year }} JobbPulse</p>
    </div>
  </footer>
</template>
