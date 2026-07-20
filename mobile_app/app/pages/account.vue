<template>
  <div>
    <header style="padding: 16px; background: var(--jp-surface); border-bottom: 1px solid var(--jp-border);">
      <div class="wordmark">Job<span>Pulse</span></div>
      <div class="muted">Account</div>
    </header>
    <div class="page-body">
      <div class="card">
        <p class="muted" style="margin: 0;">
          Auth, company profile, and onboarding land in Phase 1.
        </p>
      </div>
    </div>
    <nav class="bottom-nav">
      <NuxtLink to="/">Jobs</NuxtLink>
      <NuxtLink to="/create">Capture</NuxtLink>
      <NuxtLink to="/account" class="active">Account</NuxtLink>
    </nav>
  </div>
</template>
