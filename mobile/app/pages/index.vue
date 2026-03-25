<template>
  <div class="page-with-tabs">
    <!-- Header -->
    <div style="padding: 12px 16px 8px; display: flex; align-items: center; justify-content: space-between;">
      <div>
        <div class="wordmark" style="font-size: 20px; letter-spacing: -0.3px;">Job<span>Pulse</span></div>
        <div style="font-size: 12px; color: var(--jp-text-secondary);">Good morning</div>
      </div>
      <div style="width: 34px; height: 34px; border-radius: 50%; background: var(--jp-primary); display: flex; align-items: center; justify-content: center; font-size: 13px; color: white; font-weight: 500; cursor: pointer;">
        JP
      </div>
    </div>

    <!-- Content -->
    <div class="content">
      <!-- Metrics -->
      <div class="metric-row">
        <div class="metric-card">
          <div class="metric-label">This month</div>
          <div class="metric-value">{{ stats.jobs_this_month }}</div>
          <div class="metric-sub">Jobs posted</div>
        </div>
        <div class="metric-card">
          <div class="metric-label">Reach</div>
          <div class="metric-value">{{ formatNumber(stats.total_impressions) }}</div>
          <div class="metric-sub">Total impressions</div>
        </div>
      </div>

      <!-- Recent Jobs -->
      <div style="display: flex; align-items: center; justify-content: space-between; margin-top: 4px;">
        <div class="section-head">Recent jobs</div>
        <span style="font-size: 12px; color: var(--jp-primary); cursor: pointer;">See all</span>
      </div>

      <div v-if="jobs.length === 0" style="text-align: center; padding: 32px 16px; color: var(--jp-text-secondary); font-size: 13px;">
        No jobs yet. Tap + to capture your first job!
      </div>

      <div
        v-for="job in jobs"
        :key="job.id"
        class="job-card"
        @click="navigateToJob(job)"
      >
        <div class="job-thumb">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
            <rect x="3" y="8" width="18" height="12" rx="2" fill="#185FA5" opacity="0.2"/>
            <rect x="7" y="5" width="10" height="5" rx="1" fill="#185FA5" opacity="0.4"/>
            <circle cx="8.5" cy="14.5" r="1.5" fill="#185FA5"/>
          </svg>
        </div>
        <div class="job-info">
          <div class="job-name">{{ job.title || job.job_type }}{{ job.city ? ` — ${job.city}` : '' }}</div>
          <div class="job-meta">
            {{ formatDate(job.created_at) }} · {{ job.photo_count }} photo{{ job.photo_count !== 1 ? 's' : '' }}
            <template v-if="job.has_voice"> · Voice note</template>
          </div>
        </div>
        <span :class="['status-badge', getBadgeClass(job.status)]">{{ getBadgeLabel(job.status) }}</span>
      </div>
    </div>

    <!-- FAB -->
    <button class="fab" @click="navigateTo('/new-job')">
      <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
        <path d="M10 4V16M4 10H16" stroke="white" stroke-width="2" stroke-linecap="round"/>
      </svg>
    </button>

    <!-- Bottom Tabs -->
    <div class="bottom-tab">
      <div class="tab-item active">
        <svg class="tab-icon" viewBox="0 0 22 22" fill="none">
          <rect x="3" y="11" width="7" height="8" rx="1.5" fill="#185FA5"/>
          <rect x="12" y="3" width="7" height="16" rx="1.5" fill="#185FA5" opacity="0.4"/>
        </svg>
        <span class="tab-label" style="color: var(--jp-primary);">Home</span>
      </div>
      <div class="tab-item" @click="navigateTo('/new-job')">
        <svg class="tab-icon" viewBox="0 0 22 22" fill="none">
          <circle cx="11" cy="11" r="8" stroke="var(--jp-border)" stroke-width="1.5"/>
          <path d="M11 7V15M7 11H15" stroke="var(--jp-border)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span class="tab-label">New job</span>
      </div>
      <div class="tab-item">
        <svg class="tab-icon" viewBox="0 0 22 22" fill="none">
          <path d="M3 17V7L11 3L19 7V17L11 21L3 17Z" stroke="var(--jp-border)" stroke-width="1.5"/>
          <circle cx="11" cy="12" r="2" stroke="var(--jp-border)" stroke-width="1.5"/>
        </svg>
        <span class="tab-label">Analytics</span>
      </div>
      <div class="tab-item">
        <svg class="tab-icon" viewBox="0 0 22 22" fill="none">
          <circle cx="11" cy="8" r="3.5" stroke="var(--jp-border)" stroke-width="1.5"/>
          <path d="M4 19C4 15.686 7.134 13 11 13C14.866 13 18 15.686 18 19" stroke="var(--jp-border)" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <span class="tab-label">Profile</span>
      </div>
    </div>
  </div>
</template>

<script setup>
const api = useApi()

const jobs = ref([])
const stats = ref({ jobs_this_month: 0, total_impressions: 0, published_count: 0, total_jobs: 0 })

const loadData = async () => {
  try {
    const [jobList, jobStats] = await Promise.all([
      api.getJobs(),
      api.getStats(),
    ])
    jobs.value = jobList
    stats.value = jobStats
  } catch (err) {
    console.error('Failed to load dashboard:', err)
  }
}

onMounted(loadData)

const navigateToJob = (job) => {
  if (job.status === 'draft' || job.status === 'published') {
    navigateTo(`/jobs/${job.id}`)
  }
}

const getBadgeClass = (status) => {
  switch (status) {
    case 'published': return 'badge-success'
    case 'draft': return 'badge-pending'
    default: return 'badge-draft'
  }
}

const getBadgeLabel = (status) => {
  switch (status) {
    case 'published': return 'Published'
    case 'draft': return 'Drafts ready'
    case 'processing': return 'Processing'
    case 'pending': return 'Pending'
    default: return 'Incomplete'
  }
}

const formatDate = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffMs = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffMs / 86400000)

  if (diffDays === 0) return 'Today'
  if (diffDays === 1) return 'Yesterday'
  if (diffDays < 7) return `${diffDays} days ago`
  return date.toLocaleDateString()
}

const formatNumber = (num) => {
  if (num >= 1000) return (num / 1000).toFixed(1) + 'k'
  return String(num)
}
</script>
