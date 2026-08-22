<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const open = ref(false)

const nav = [
  { to: '/services', label: 'Services' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/service-areas', label: 'Service areas' },
  { to: '/about', label: 'About' },
  { to: '/faq', label: 'FAQ' },
  { to: '/contact', label: 'Contact' },
]

function close() {
  open.value = false
}
</script>

<template>
  <div class="chrome">
    <a class="phone-bar" :href="`tel:${phoneTel}`">
      <span class="phone-bar__copy">Call now — we answer:</span>
      <strong>{{ phone }}</strong>
      <span class="phone-bar__tap">TAP TO CALL</span>
    </a>

    <header class="site-header">
      <div class="container site-header__inner">
        <NuxtLink class="brand" to="/" @click="close">
          <span class="brand__mark" aria-hidden="true">ABC</span>
          <span class="brand__text">
            <span class="brand__name">ABC Painters</span>
            <span class="brand__sub">Acworth, GA</span>
          </span>
        </NuxtLink>

        <nav class="nav-desktop" aria-label="Primary">
          <NuxtLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-desktop__link">
            {{ item.label }}
          </NuxtLink>
        </nav>

        <div class="site-header__actions">
          <NuxtLink class="btn btn--primary site-header__cta" to="/contact">Free estimate</NuxtLink>
          <button
            type="button"
            class="nav-toggle"
            :aria-expanded="open"
            aria-controls="mobile-nav"
            @click="open = !open"
          >
            <span class="sr-only">Menu</span>
            <span class="nav-toggle__bar" />
            <span class="nav-toggle__bar" />
            <span class="nav-toggle__bar" />
          </button>
        </div>
      </div>

      <div v-if="open" id="mobile-nav" class="nav-mobile">
        <NuxtLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-mobile__link" @click="close">
          {{ item.label }}
        </NuxtLink>
        <a class="nav-mobile__call" :href="`tel:${phoneTel}`" @click="close">Call {{ phone }}</a>
      </div>
    </header>
  </div>
</template>

<style scoped>
.chrome {
  position: sticky;
  top: 0;
  z-index: 40;
}

.phone-bar {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  height: var(--phone-bar-h);
  background: var(--orange);
  color: #fff !important;
  font-weight: 700;
  text-decoration: none !important;
  font-size: 1rem;
}

.phone-bar:hover {
  background: var(--orange-hover);
}

.phone-bar strong {
  font-weight: 800;
  font-size: 1.125rem;
}

.phone-bar__tap {
  display: none;
  margin-left: auto;
  padding-right: 1rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.04em;
}

.site-header {
  height: var(--header-h);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
}

.site-header__inner {
  height: var(--header-h);
  display: flex;
  align-items: center;
  gap: 1rem;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  text-decoration: none !important;
  color: var(--ink);
}

.brand__mark {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: var(--radius);
  background: var(--navy);
  color: #fff;
  font-weight: 800;
  font-size: 0.7rem;
  display: grid;
  place-items: center;
  letter-spacing: 0.02em;
}

.brand__text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand__name {
  font-weight: 800;
  font-size: 1rem;
  color: var(--navy);
}

.brand__sub {
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 600;
}

.nav-desktop {
  display: none;
  flex: 1;
  justify-content: center;
  gap: 0.15rem;
}

.nav-desktop__link {
  padding: 0.4rem 0.6rem;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--ink);
  text-decoration: none !important;
}

.nav-desktop__link:hover,
.nav-desktop__link.router-link-active {
  color: var(--orange);
  text-decoration: underline;
  text-underline-offset: 6px;
}

.site-header__actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-left: auto;
}

.site-header__cta {
  display: none;
}

.nav-toggle {
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  background: var(--surface);
  display: grid;
  place-content: center;
  gap: 4px;
  cursor: pointer;
}

.nav-toggle__bar {
  display: block;
  width: 1.1rem;
  height: 2px;
  background: var(--navy);
}

.nav-mobile {
  border-top: 1px solid var(--border);
  background: var(--bg);
  padding: 0.5rem 1rem 1rem;
  display: grid;
}

.nav-mobile__link {
  padding: 0.85rem 0.25rem;
  font-weight: 700;
  font-size: 1.25rem;
  color: var(--ink);
  text-decoration: none !important;
  border-bottom: 1px solid var(--border);
}

.nav-mobile__call {
  margin-top: 0.75rem;
  display: flex;
  justify-content: center;
  padding: 0.9rem;
  background: var(--orange);
  color: #fff !important;
  font-weight: 800;
  text-decoration: none !important;
  border-radius: var(--radius);
}

@media (max-width: 959px) {
  .phone-bar {
    justify-content: flex-start;
    padding-left: 1rem;
  }
  .phone-bar__copy {
    display: none;
  }
  .phone-bar__tap {
    display: inline;
  }
}

@media (min-width: 960px) {
  .nav-desktop {
    display: flex;
  }
  .site-header__cta {
    display: inline-flex;
  }
  .nav-toggle,
  .nav-mobile {
    display: none;
  }
}
</style>
