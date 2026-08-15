<script setup lang="ts">
const config = useRuntimeConfig()
const appUrl = config.public.appUrl as string
const open = ref(false)

const nav = [
  { href: '/#how-it-works', label: 'How it works' },
  { href: '/#what-you-get', label: 'What you get' },
  { href: '/#lead-desk', label: 'Lead Desk' },
]

function close() {
  open.value = false
}
</script>

<template>
  <header class="site-header">
    <div class="container header-inner">
      <NuxtLink class="brand" to="/" @click="close">
        <span class="brand-mark" aria-hidden="true">JP</span>
        <span class="brand-name">Jobb<span>Pulse</span></span>
      </NuxtLink>

      <nav class="nav-desktop" aria-label="Primary">
        <a v-for="item in nav" :key="item.href" :href="item.href">{{ item.label }}</a>
      </nav>

      <div class="header-actions">
        <a class="link-quiet" :href="appUrl">Sign in</a>
        <a class="btn btn-primary" href="#demo">See JobbPulse in action</a>
        <button
          type="button"
          class="nav-toggle"
          :aria-expanded="open"
          aria-controls="mobile-nav"
          @click="open = !open"
        >
          <span class="sr-only">Menu</span>
          <span />
          <span />
          <span />
        </button>
      </div>
    </div>

    <nav v-if="open" id="mobile-nav" class="nav-mobile" aria-label="Mobile">
      <a v-for="item in nav" :key="item.href" :href="item.href" @click="close">{{ item.label }}</a>
      <a :href="appUrl" @click="close">Sign in</a>
      <a class="btn btn-primary" href="#demo" @click="close">See JobbPulse in action</a>
    </nav>
  </header>
</template>
