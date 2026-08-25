<script setup lang="ts">
const config = useRuntimeConfig()
const phone = config.public.phone as string
const phoneTel = config.public.phoneTel as string
const open = ref(false)
const scrolled = ref(false)

const nav = [
  { to: '/', label: 'Home' },
  { to: '/services', label: 'Services' },
  { to: '/work', label: 'Work' },
  { to: '/service-area', label: 'Areas' },
  { to: '/about', label: 'About' },
  { to: '/contact', label: 'Contact' },
]

function close() {
  open.value = false
}

function onScroll() {
  scrolled.value = window.scrollY > 40
}

onMounted(() => {
  onScroll()
  window.addEventListener('scroll', onScroll, { passive: true })
})
onBeforeUnmount(() => window.removeEventListener('scroll', onScroll))

watch(open, (v) => {
  if (!import.meta.client) return
  document.body.style.overflow = v ? 'hidden' : ''
})
</script>

<template>
  <header class="site-header" :class="{ 'site-header--scrolled': scrolled }">
    <div class="container site-header__inner">
      <NuxtLink class="brand" to="/" @click="close">
        <span class="brand__name">Red Clay</span>
        <span class="brand__sub">Painting · Metro Atlanta</span>
      </NuxtLink>

      <nav class="nav-desktop" aria-label="Primary">
        <NuxtLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-desktop__link">
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="site-header__actions">
        <a class="site-header__phone" :href="`tel:${phoneTel}`">{{ phone }}</a>
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

    <div v-if="open" id="mobile-nav" class="nav-mobile" role="dialog" aria-label="Menu">
      <NuxtLink v-for="item in nav" :key="item.to" :to="item.to" class="nav-mobile__link" @click="close">
        {{ item.label }}
      </NuxtLink>
      <a class="btn btn--primary" :href="`tel:${phoneTel}`" @click="close">Call {{ phone }}</a>
    </div>
  </header>
</template>

<style scoped>
.site-header {
  position: sticky;
  top: 0;
  z-index: 40;
  height: var(--header-h);
  background: var(--page);
  border-bottom: 1px solid var(--border);
  transition: box-shadow 0.3s;
}

.site-header--scrolled {
  box-shadow: 0 8px 24px rgba(43, 40, 37, 0.08);
}

.site-header__inner {
  height: var(--header-h);
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.brand {
  display: flex;
  flex-direction: column;
  text-decoration: none !important;
  color: var(--charcoal);
  min-width: 0;
}

.brand__name {
  font-family: var(--serif);
  font-size: 1.5rem;
  font-weight: 500;
  line-height: 1.1;
}

.brand__sub {
  font-size: 0.72rem;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--muted);
}

.nav-desktop {
  display: none;
  gap: 1.75rem;
  margin-left: auto;
}

.nav-desktop__link {
  color: var(--ink);
  font-weight: 500;
  text-decoration: none !important;
  padding: 0.35rem 0;
}

.nav-desktop__link:hover,
.nav-desktop__link.router-link-active {
  color: var(--clay);
  box-shadow: inset 0 -2px 0 var(--clay);
}

.site-header__actions {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  margin-left: auto;
}

.site-header__phone {
  display: none;
  color: var(--clay);
  font-weight: 600;
  text-decoration: none !important;
  min-height: 44px;
  align-items: center;
}

.nav-toggle {
  width: 44px;
  height: 44px;
  border: 0;
  background: transparent;
  display: grid;
  place-content: center;
  gap: 5px;
  cursor: pointer;
}

.nav-toggle__bar {
  display: block;
  width: 22px;
  height: 2px;
  background: var(--charcoal);
}

.nav-mobile {
  position: fixed;
  inset: 0;
  background: var(--charcoal);
  z-index: 45;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 1.25rem;
  padding: 2rem;
}

.nav-mobile__link {
  font-family: var(--serif);
  font-size: 1.375rem;
  color: var(--page);
  text-decoration: none !important;
}

@media (min-width: 1024px) {
  .nav-desktop {
    display: flex;
  }
  .site-header__phone {
    display: inline-flex;
  }
  .nav-toggle,
  .nav-mobile {
    display: none;
  }
  .site-header__actions {
    margin-left: 0;
  }
}
</style>
