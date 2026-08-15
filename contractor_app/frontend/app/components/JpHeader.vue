<script setup lang="ts">
const props = withDefaults(
  defineProps<{
    showBack?: boolean
    backTo?: string
    showMenu?: boolean
  }>(),
  {
    showBack: false,
    backTo: '',
    showMenu: true,
  },
)

const router = useRouter()
const menuOpen = ref(false)

function goBack() {
  if (props.backTo) {
    router.push(props.backTo)
    return
  }
  if (import.meta.client && window.history.length > 1) router.back()
  else router.push('/jobs')
}
</script>

<template>
  <header class="jp-header">
    <div class="jp-header__side">
      <button
        v-if="showBack"
        type="button"
        class="icon-btn"
        aria-label="Go back"
        @click="goBack"
      >
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
          <path
            d="M15 18l-6-6 6-6"
            stroke="currentColor"
            stroke-width="2.2"
            stroke-linecap="round"
            stroke-linejoin="round"
          />
        </svg>
      </button>
    </div>

    <NuxtLink to="/jobs" class="wordmark" aria-label="JobbPulse home">
      Jobb<span>Pulse</span>
    </NuxtLink>

    <div class="jp-header__side jp-header__side--end">
      <div v-if="showMenu" class="menu-wrap">
        <button
          type="button"
          class="icon-btn"
          aria-label="Open menu"
          aria-haspopup="true"
          :aria-expanded="menuOpen"
          @click="menuOpen = !menuOpen"
        >
          <svg width="22" height="22" viewBox="0 0 24 24" fill="none" aria-hidden="true">
            <path
              d="M4 7h16M4 12h16M4 17h16"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
            />
          </svg>
        </button>
        <div v-if="menuOpen" class="menu-dropdown" role="menu">
          <NuxtLink to="/jobs" role="menuitem" @click="menuOpen = false">My Jobs</NuxtLink>
          <NuxtLink to="/settings" role="menuitem" @click="menuOpen = false">Settings</NuxtLink>
        </div>
      </div>
    </div>
  </header>
</template>

<style scoped>
.jp-header {
  position: sticky;
  top: 0;
  z-index: 20;
  display: grid;
  grid-template-columns: 48px 1fr 48px;
  align-items: center;
  min-height: calc(var(--jp-header-h) + var(--jp-safe-top));
  padding: var(--jp-safe-top) 8px 0;
  background: rgba(10, 10, 10, 0.92);
  backdrop-filter: blur(10px);
}

.jp-header .wordmark {
  text-align: center;
  justify-self: center;
}

.jp-header__side {
  display: flex;
  align-items: center;
  min-height: 44px;
}

.jp-header__side--end {
  justify-content: flex-end;
}

.icon-btn {
  width: 44px;
  height: 44px;
  border: none;
  background: transparent;
  color: var(--jp-text);
  border-radius: 12px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.menu-wrap {
  position: relative;
}

.menu-dropdown {
  position: absolute;
  right: 0;
  top: 100%;
  min-width: 160px;
  background: var(--jp-card);
  border: 1px solid var(--jp-card-border);
  border-radius: 12px;
  padding: 6px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.45);
}

.menu-dropdown a {
  display: block;
  padding: 12px 14px;
  border-radius: 8px;
  font-weight: 600;
  min-height: 44px;
}

.menu-dropdown a:hover {
  background: var(--jp-bg-elevated);
}
</style>
