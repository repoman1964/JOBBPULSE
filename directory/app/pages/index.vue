<template>
  <div class="shell">
    <header class="header">
      <div class="wordmark">Job<span>Pulse</span> Directory</div>
      <span class="muted" style="font-size: 13px;">Phase 0 scaffold</span>
    </header>

    <section class="hero">
      <h1>Local proof of completed work</h1>
      <p class="muted">
        The JobPulse directory is an owned destination for contractor project pages —
        before-and-after photos, project summaries, and profiles. Public contractor and
        project routes land in Phase 6.
      </p>

      <div class="grid">
        <div class="tile">
          <strong>Contractors</strong>
          <span class="muted">/contractors/{state}/{city}/{slug}</span>
        </div>
        <div class="tile">
          <strong>Projects</strong>
          <span class="muted">/projects/{state}/{city}/{service}/{slug}</span>
        </div>
        <div class="tile">
          <strong>Privacy</strong>
          <span class="muted">City-level location only — no exact addresses</span>
        </div>
      </div>
    </section>
  </div>
</template>
