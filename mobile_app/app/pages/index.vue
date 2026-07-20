<template>
  <div>
    <header style="padding: 16px 16px 8px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div class="wordmark" style="font-size: 22px;">Job<span>Pulse</span></div>
        <div class="muted">{{ greeting }}, {{ firstName }}</div>
      </div>
      <button
        type="button"
        class="avatar"
        @click="navigateTo('/account')"
      >
        {{ initials }}
      </button>
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600; margin-bottom: 4px;">{{ companyName }}</div>
        <div class="muted" style="margin-bottom: 12px;">
          Role: {{ roleLabel }} · Phase 1 foundation ready
        </div>
        <div class="perm-row">
          <span :class="['pill', permissions?.can_create_jobs ? 'on' : 'off']">Create jobs</span>
          <span :class="['pill', permissions?.can_approve_and_publish ? 'on' : 'off']">Approve / publish</span>
          <span :class="['pill', permissions?.can_manage_team ? 'on' : 'off']">Manage team</span>
        </div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <h1 style="margin: 0 0 8px; font-size: 18px;">Jobs come next</h1>
        <p class="muted" style="margin: 0 0 16px;">
          Phase 2 will let you create a job, capture before photos, and resume later for after photos.
        </p>
        <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/create')">
          Preview create flow
        </button>
      </div>

      <div v-if="company && !company.onboarding_completed" class="card">
        <p class="muted" style="margin: 0 0 12px;">Finish company setup to personalize content tone and services.</p>
        <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/onboarding')">
          Continue onboarding
        </button>
      </div>
    </div>

    <button class="fab" type="button" aria-label="Create job" @click="navigateTo('/create')">+</button>

    <nav class="bottom-nav">
      <NuxtLink to="/" class="active">Jobs</NuxtLink>
      <NuxtLink to="/create">Capture</NuxtLink>
      <NuxtLink to="/account">Account</NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const api = useApi()

const user = computed(() => auth.user.value)
const company = computed(() => auth.company.value)
const permissions = computed(() => auth.permissions.value)

const firstName = computed(() => user.value?.full_name?.split(' ')[0] || 'there')
const companyName = computed(() => company.value?.name || 'Your company')
const roleLabel = computed(() => permissions.value?.role || membershipRole.value || 'member')
const membershipRole = computed(() => auth.membership.value?.role)

const initials = computed(() => {
  const parts = (user.value?.full_name || 'JP').split(' ').filter(Boolean)
  return ((parts[0]?.[0] || 'J') + (parts[1]?.[0] || 'P')).toUpperCase()
})

const hour = new Date().getHours()
const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

onMounted(async () => {
  if (!user.value && auth.accessToken.value) {
    try {
      const me = (await api.me()) as any
      auth.user.value = me.user
      auth.company.value = me.company
      auth.membership.value = me.membership
      auth.permissions.value = me.permissions
    } catch {
      // middleware / plugin handle session expiry
    }
  }
})
</script>

<style scoped>
.avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: none;
  background: var(--jp-primary);
  color: #fff;
  font-weight: 600;
  font-size: 13px;
  cursor: pointer;
}
.perm-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}
.pill {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 999px;
  font-weight: 600;
}
.pill.on {
  background: #e8f5ee;
  color: var(--jp-success);
}
.pill.off {
  background: #f1f5f9;
  color: var(--jp-text-secondary);
}
.bottom-nav a.active {
  color: var(--jp-primary);
}
</style>
