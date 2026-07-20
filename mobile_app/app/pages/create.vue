<template>
  <div>
    <header style="padding: 12px 16px; display: flex; align-items: center; gap: 12px; background: var(--jp-surface); border-bottom: 1px solid var(--jp-border);">
      <NuxtLink to="/" class="muted">← Back</NuxtLink>
      <div style="font-weight: 600;">Create Job</div>
    </header>

    <div class="page-body">
      <div class="card">
        <h1 style="margin: 0 0 8px; font-size: 18px;">Coming in Phase 2</h1>
        <p class="muted" style="margin: 0 0 12px;">
          You’re signed in as <strong>{{ auth.user.value?.full_name }}</strong>
          ({{ auth.permissions.value?.role || 'member' }}). Job capture with before/after photos ships next.
        </p>
        <ol class="muted" style="margin: 0; padding-left: 18px; line-height: 1.6;">
          <li>Tap create → take before photos</li>
          <li>Save and leave the site</li>
          <li>Return → after photos + voice</li>
          <li>Generate → review → approve → publish</li>
        </ol>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const auth = useAuth()
</script>
