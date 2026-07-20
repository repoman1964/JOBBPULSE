<template>
  <div>
    <header style="padding: 16px 16px 8px; display: flex; justify-content: space-between; align-items: center;">
      <div>
        <div class="wordmark" style="font-size: 22px;">Job<span>Pulse</span></div>
        <div class="muted">{{ greeting }}, {{ firstName }}</div>
      </div>
      <button type="button" class="avatar" @click="navigateTo('/account')">
        {{ initials }}
      </button>
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600; margin-bottom: 2px;">{{ companyName }}</div>
        <div class="muted">{{ roleLabel }}</div>
      </div>

      <!-- Continue job -->
      <div v-if="resumeJob" class="card resume-card" style="margin-bottom: 12px;">
        <div class="muted" style="font-size: 12px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.04em;">
          Continue job
        </div>
        <h2 style="margin: 6px 0 4px; font-size: 18px;">{{ resumeJob.title }}</h2>
        <div class="mini-timeline" style="margin: 10px 0 12px;">
          <div
            v-for="(step, i) in resumeJob.timeline"
            :key="step.key"
            class="mini-step"
            :class="step.status"
          >
            <span class="dot" />
            <span class="mini-label">{{ step.label }}</span>
            <span v-if="i < resumeJob.timeline.length - 1" class="mini-line" />
          </div>
        </div>
        <p style="margin: 0 0 8px; font-size: 14px;">
          <strong>{{ resumeJob.next_action.label }}</strong>
          <span class="muted"> — {{ resumeJob.next_action.reason }}</span>
        </p>
        <p v-if="resumeJob.next_action.optional_tip" class="muted" style="margin: 0 0 12px; font-size: 12px;">
          {{ resumeJob.next_action.optional_tip }}
        </p>
        <button class="btn btn-primary btn-block" type="button" @click="openJob(resumeJob.id)">
          {{ resumeJob.next_action.cta }}
        </button>
      </div>

      <div v-else class="card" style="margin-bottom: 12px;">
        <h1 style="margin: 0 0 8px; font-size: 18px;">No jobs yet</h1>
        <p class="muted" style="margin: 0 0 16px;">
          Name the job, add after photos when work is done, then a short voice note.
          Before photos are optional if you forget.
        </p>
        <button class="btn btn-primary btn-block" type="button" @click="navigateTo('/create')">
          Create Job
        </button>
      </div>

      <div v-if="company && !company.onboarding_completed" class="card" style="margin-bottom: 12px;">
        <p class="muted" style="margin: 0 0 12px;">Finish company setup to personalize tone and services.</p>
        <button class="btn btn-block" type="button" style="background: #e8eef5; color: var(--jp-primary);" @click="navigateTo('/onboarding')">
          Continue onboarding
        </button>
      </div>

      <div v-if="jobs.length" style="margin-top: 4px;">
        <div class="section-label">Your jobs</div>
        <div v-if="loading" class="muted" style="padding: 8px 0;">Loading…</div>
        <div v-else class="job-list">
          <button
            v-for="job in jobs"
            :key="job.id"
            type="button"
            class="job-card"
            @click="openJob(job.id)"
          >
            <div class="job-card-top">
              <div class="job-title">{{ job.title }}</div>
              <span class="status-badge">{{ statusLabel(job.status) }}</span>
            </div>
            <div class="muted" style="font-size: 13px; margin-top: 4px;">
              {{ job.photo_counts.before }} before · {{ job.photo_counts.after }} after
              <template v-if="job.city"> · {{ job.city }}</template>
            </div>
            <div class="next-line">
              Next: {{ job.next_action.label }}
            </div>
          </button>
        </div>
      </div>

      <p v-if="error" class="error-text">{{ error }}</p>
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
const { jobs, loading, error, resumeJob, fetchJobs, statusLabel } = useJobs()

const user = computed(() => auth.user.value)
const company = computed(() => auth.company.value)
const permissions = computed(() => auth.permissions.value)

const firstName = computed(() => user.value?.full_name?.split(' ')[0] || 'there')
const companyName = computed(() => company.value?.name || 'Your company')
const roleLabel = computed(() => permissions.value?.role || auth.membership.value?.role || 'member')

const initials = computed(() => {
  const parts = (user.value?.full_name || 'JP').split(' ').filter(Boolean)
  return ((parts[0]?.[0] || 'J') + (parts[1]?.[0] || 'P')).toUpperCase()
})

const hour = new Date().getHours()
const greeting = hour < 12 ? 'Good morning' : hour < 18 ? 'Good afternoon' : 'Good evening'

function openJob(id: string) {
  const job = jobs.value.find((j) => j.id === id)
  if (job?.next_action?.action === 'record_voice_summary') {
    navigateTo(`/jobs/${id}#voice`)
    return
  }
  navigateTo(`/jobs/${id}`)
}

onMounted(async () => {
  if (!user.value && auth.accessToken.value) {
    try {
      const me = (await api.me()) as any
      auth.user.value = me.user
      auth.company.value = me.company
      auth.membership.value = me.membership
      auth.permissions.value = me.permissions
    } catch {
      // middleware handles session expiry
    }
  }
  try {
    await fetchJobs()
  } catch {
    // error state set in composable
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
.resume-card {
  border-color: #b7d0ea;
  background: linear-gradient(180deg, #f0f7fc 0%, #fff 70%);
}
.mini-timeline {
  display: flex;
  align-items: flex-start;
  gap: 0;
  overflow-x: auto;
}
.mini-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  min-width: 52px;
  flex: 1;
}
.mini-step .dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #cbd5e1;
  border: 2px solid #e2e8f0;
}
.mini-step.complete .dot {
  background: var(--jp-success);
  border-color: var(--jp-success);
}
.mini-step.current .dot {
  background: var(--jp-primary);
  border-color: var(--jp-primary);
  box-shadow: 0 0 0 3px rgba(24, 95, 165, 0.2);
}
.mini-step.locked .dot {
  background: #f1f5f9;
  border-color: #e2e8f0;
}
.mini-step.optional .dot {
  background: #fff;
  border-color: #94a3b8;
  border-style: dashed;
}
.mini-step.skipped .dot {
  background: #e2e8f0;
  border-color: #cbd5e1;
}
.mini-label {
  font-size: 10px;
  color: var(--jp-text-secondary);
  margin-top: 4px;
  text-align: center;
}
.mini-step.current .mini-label {
  color: var(--jp-primary);
  font-weight: 700;
}
.mini-line {
  position: absolute;
  top: 5px;
  left: calc(50% + 8px);
  width: calc(100% - 16px);
  height: 2px;
  background: #e2e8f0;
  z-index: 0;
}
.mini-step.complete .mini-line {
  background: #a7f3d0;
}
.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--jp-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 8px 0 10px;
}
.job-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}
.job-card {
  width: 100%;
  text-align: left;
  background: var(--jp-surface);
  border: 1px solid var(--jp-border);
  border-radius: var(--jp-radius);
  padding: 14px;
  cursor: pointer;
}
.job-card-top {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}
.job-title {
  font-weight: 600;
  font-size: 15px;
}
.status-badge {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  padding: 3px 8px;
  border-radius: 999px;
  background: #eef2f6;
  color: var(--jp-text-secondary);
}
.next-line {
  margin-top: 8px;
  font-size: 13px;
  font-weight: 600;
  color: var(--jp-primary);
}
.error-text {
  color: var(--jp-danger);
  font-size: 14px;
}
.bottom-nav a.active {
  color: var(--jp-primary);
}
</style>
