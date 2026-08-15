<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const open = ref(false)

const nav = [
  { to: '/services', label: 'Services' },
  { to: '/portfolio', label: 'Portfolio' },
  { to: '/service-area', label: 'Service area' },
  { to: '/about', label: 'About' },
  { to: '/reviews', label: 'Reviews' },
  { to: '/faq', label: 'FAQ' },
  { to: '/contact', label: 'Contact' },
]

function close() {
  open.value = false
}
</script>

<template>
  <header class="site-header">
    <div class="container site-header__inner">
      <NuxtLink class="brand" to="/" @click="close">
        <span class="brand__mark" aria-hidden="true">RC</span>
        <span class="brand__text">
          <span class="brand__name">Red Clay</span>
          <span class="brand__sub">Cabinet Installers</span>
        </span>
      </NuxtLink>

      <nav class="nav-desktop" aria-label="Primary">
        <NuxtLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-desktop__link">
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="site-header__actions">
        <a class="site-header__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
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
      <a class="nav-mobile__link" :href="`tel:${phoneTel}`" @click="close">Call {{ phone }}</a>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  height: var(--header-h);
  background: rgba(250, 247, 244, 0.92);
  backdrop-filter: blur(10px);
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
  min-width: 0;
}

.brand__mark {
  width: 2.35rem;
  height: 2.35rem;
  border-radius: 10px;
  background: var(--clay);
  color: #fff;
  font-weight: 800;
  font-size: 0.85rem;
  display: grid;
  place-items: center;
  flex-shrink: 0;
}

.brand__text {
  display: flex;
  flex-direction: column;
  line-height: 1.1;
}

.brand__name {
  font-weight: 800;
  font-size: 1rem;
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
  padding: 0.4rem 0.55rem;
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--muted);
  text-decoration: none !important;
  border-radius: 8px;
}

.nav-desktop__link:hover,
.nav-desktop__link.router-link-active {
  color: var(--clay-deep);
  background: var(--clay-soft);
}

.site-header__actions {
  display: flex;
  align-items: center;
  gap: 0.65rem;
  margin-left: auto;
}

.site-header__phone {
  display: none;
  font-weight: 700;
  color: var(--ink);
  text-decoration: none !important;
  font-size: 0.92rem;
}

.site-header__cta {
  display: none;
}

.nav-toggle {
  width: 2.5rem;
  height: 2.5rem;
  border: 1px solid var(--border);
  border-radius: 10px;
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
  background: var(--ink);
  border-radius: 2px;
}

.nav-mobile {
  border-top: 1px solid var(--border);
  background: var(--surface);
  padding: 0.5rem 1rem 1rem;
  display: grid;
}

.nav-mobile__link {
  padding: 0.75rem 0.25rem;
  font-weight: 600;
  color: var(--ink);
  text-decoration: none !important;
  border-bottom: 1px solid var(--border);
}

@media (min-width: 960px) {
  .nav-desktop {
    display: flex;
  }
  .site-header__phone,
  .site-header__cta {
    display: inline-flex;
  }
  .nav-toggle,
  .nav-mobile {
    display: none;
  }
}
</style>
