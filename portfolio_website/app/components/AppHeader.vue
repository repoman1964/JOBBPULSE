<script setup lang="ts">
const navOpen = ref(false)

const links = [
  { to: '/projects', label: 'Browse Projects' },
  { to: '/services', label: 'Services' },
  { to: '/locations', label: 'Locations' },
  { to: '/contractors', label: 'Contractors' },
  { to: '/how-it-works', label: 'How It Works' },
]

function closeNav() {
  navOpen.value = false
}
</script>

<template>
  <header class="site-header">
    <div class="container site-header__inner">
      <NuxtLink to="/" class="logo" @click="closeNav">
        <span class="logo__mark" aria-hidden="true">
          <svg width="28" height="28" viewBox="0 0 28 28" fill="none" xmlns="http://www.w3.org/2000/svg">
            <rect x="2" y="2" width="24" height="24" rx="7" stroke="currentColor" stroke-width="2" />
            <path
              d="M9 14.5c1.2-2.8 2.4-4.2 5-4.2 2.2 0 3.4 1.4 3.4 3.2 0 3.6-5.4 4-5.4 7"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
            <circle cx="14" cy="22" r="1.2" fill="currentColor" />
          </svg>
        </span>
        <span class="logo__text">JobPulse ATL</span>
      </NuxtLink>

      <button
        type="button"
        class="nav-toggle"
        :aria-expanded="navOpen"
        aria-controls="primary-nav"
        @click="navOpen = !navOpen"
      >
        <span class="sr-only">Menu</span>
        <span class="nav-toggle__bars" :class="{ 'is-open': navOpen }" />
      </button>

      <nav id="primary-nav" class="nav" :class="{ 'nav--open': navOpen }" aria-label="Primary">
        <NuxtLink v-for="link in links" :key="link.to" :to="link.to" @click="closeNav">
          {{ link.label }}
        </NuxtLink>
      </nav>

      <NuxtLink class="btn btn-outline nav__cta" to="/for-contractors" @click="closeNav">
        Contractor Login
      </NuxtLink>
    </div>
  </header>
</template>
