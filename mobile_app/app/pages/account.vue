<template>
  <div>
    <header style="padding: 16px; background: var(--jp-surface); border-bottom: 1px solid var(--jp-border);">
      <div class="wordmark">Job<span>Pulse</span></div>
      <div class="muted">Account</div>
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600;">{{ user?.full_name }}</div>
        <div class="muted">{{ user?.email }}</div>
        <div class="muted" style="margin-top: 8px;">{{ company?.name }} · {{ membership?.role }}</div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600; margin-bottom: 8px;">Permissions</div>
        <ul class="muted" style="margin: 0; padding-left: 18px; line-height: 1.6;">
          <li>Create jobs: {{ yesNo(permissions?.can_create_jobs) }}</li>
          <li>Approve / publish: {{ yesNo(permissions?.can_approve_and_publish) }}</li>
          <li>Manage team: {{ yesNo(permissions?.can_manage_team) }}</li>
        </ul>
      </div>

      <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/onboarding')">
        Company setup
      </button>
      <button
        class="btn btn-block"
        type="button"
        style="margin-top: 10px; background: #fee2e2; color: #991b1b;"
        @click="auth.logout()"
      >
        Sign out
      </button>
    </div>

    <nav class="bottom-nav">
      <NuxtLink to="/">Jobs</NuxtLink>
      <NuxtLink to="/create">Capture</NuxtLink>
      <NuxtLink to="/account" class="active">Account</NuxtLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
const user = computed(() => auth.user.value)
const company = computed(() => auth.company.value)
const membership = computed(() => auth.membership.value)
const permissions = computed(() => auth.permissions.value)

function yesNo(v?: boolean) {
  return v ? 'Yes' : 'No'
}
</script>
