<script setup lang="ts">
import type { Company, SocialConnection } from '~/types/domain'

const api = useApi()
const { session, logout } = useAuthSession()

const company = ref<Company | null>(null)
const social = ref<SocialConnection[]>([])
const loading = ref(true)
const error = ref('')
const banner = ref('')

const platformLabel: Record<string, string> = {
  facebook: 'Facebook',
  instagram: 'Instagram',
  google_business: 'Google Business Profile',
  tiktok: 'TikTok',
  youtube: 'YouTube Shorts',
  x: 'X',
  linkedin: 'LinkedIn',
}

const statusLabel: Record<string, string> = {
  connected: 'Connected',
  not_connected: 'Not connected',
  reconnect_required: 'Reconnect required',
  connection_pending: 'Connection pending',
  provider_unavailable: 'Unavailable',
}

async function load() {
  loading.value = true
  try {
    company.value = await api.getCompany()
    social.value = await api.listSocialConnections()
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not load settings.'
  } finally {
    loading.value = false
  }
}

async function toggleNotif(key: 'contentReadyForApproval' | 'publishingComplete') {
  if (!company.value) return
  const next = {
    ...company.value.notificationSettings,
    [key]: !company.value.notificationSettings[key],
  }
  company.value = await api.updateNotificationSettings(next)
  if (session.value) session.value.company = company.value
}

async function manageSocial() {
  error.value = ''
  try {
    const { url } = await api.getSocialConnectUrl()
    // Mock returns an in-app path; real provider would be external
    if (url.startsWith('http')) {
      window.location.href = url
    } else {
      await navigateTo(url)
    }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Could not open connection flow.'
  }
}

async function signOut() {
  await logout()
  await navigateTo('/sign-in')
}

const route = useRoute()
onMounted(async () => {
  await load()
  if (route.query.connected === '1') {
    banner.value = 'Social account connection updated.'
  }
})
</script>

<template>
  <div>
    <JpHeader show-back back-to="/jobs" />
    <main class="app-main">
      <h1 class="page-title">Settings</h1>
      <div v-if="banner" class="banner">{{ banner }}</div>
      <div v-if="error" class="banner banner-error" role="alert">{{ error }}</div>
      <p v-if="loading" class="muted">Loading…</p>

      <template v-else-if="company">
        <section class="card" style="margin-top: 12px">
          <h2 class="section-label">Business profile</h2>
          <p class="biz-name">{{ company.name }}</p>
          <p class="muted" style="margin: 0 0 8px">{{ company.contactName }}</p>
          <NuxtLink class="link-lime" to="/settings/business-profile">
            Edit Business Profile ›
          </NuxtLink>
        </section>

        <section style="margin-top: 18px">
          <h2 class="section-label">Social accounts</h2>
          <p class="muted" style="margin-top: 0; font-size: 0.9rem">
            Connect once. JobbPulse handles the posting.
          </p>
          <div class="card card-tight social-card">
            <div v-for="row in social" :key="row.platform" class="social-row">
              <div>
                <strong>{{ platformLabel[row.platform] || row.platform }}</strong>
                <p v-if="row.accountName" class="muted" style="margin: 2px 0 0; font-size: 0.85rem">
                  {{ row.accountName }}
                </p>
              </div>
              <span
                class="conn"
                :class="{ on: row.status === 'connected' }"
              >
                {{ statusLabel[row.status] || row.status }}
              </span>
            </div>
            <button type="button" class="btn btn-primary" style="margin-top: 8px" @click="manageSocial">
              Manage Social Accounts
            </button>
          </div>
        </section>

        <section style="margin-top: 18px">
          <h2 class="section-label">Notifications</h2>
          <div class="card card-tight">
            <label class="toggle-row">
              <span>Content ready for approval</span>
              <input
                type="checkbox"
                :checked="company.notificationSettings.contentReadyForApproval"
                @change="toggleNotif('contentReadyForApproval')"
              />
            </label>
            <label class="toggle-row">
              <span>Publishing complete</span>
              <input
                type="checkbox"
                :checked="company.notificationSettings.publishingComplete"
                @change="toggleNotif('publishingComplete')"
              />
            </label>
          </div>
        </section>

        <button type="button" class="btn btn-secondary" style="margin-top: 20px" @click="signOut">
          Sign Out
        </button>
      </template>
    </main>
  </div>
</template>

<style scoped>
.biz-name {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 800;
}

.social-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 4px;
  border-bottom: 1px solid var(--jp-card-border);
  min-height: 56px;
}

.social-row:last-of-type {
  border-bottom: none;
}

.conn {
  color: var(--jp-text-dim);
  font-size: 0.85rem;
  font-weight: 600;
  white-space: nowrap;
}

.conn.on {
  color: var(--jp-accent);
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 52px;
  gap: 12px;
  border-bottom: 1px solid var(--jp-card-border);
  padding: 4px 0;
}

.toggle-row:last-child {
  border-bottom: none;
}

.toggle-row input {
  width: 48px;
  height: 28px;
  accent-color: var(--jp-accent);
}
</style>
