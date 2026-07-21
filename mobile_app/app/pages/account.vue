<template>
  <div>
    <header style="padding: 16px; background: var(--jp-surface); border-bottom: 1px solid var(--jp-border);">
      <div class="wordmark">Job<span>Pulse</span></div>
      <div class="muted">
        Account
        <span
          v-if="unreadCount > 0"
          style="margin-left: 8px; background: #dc2626; color: #fff; border-radius: 999px; padding: 1px 8px; font-size: 12px;"
        >
          {{ unreadCount }}
        </span>
      </div>
    </header>

    <div class="page-body">
      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600;">{{ user?.full_name }}</div>
        <div class="muted">{{ user?.email }}</div>
        <div class="muted" style="margin-top: 8px;">{{ company?.name }} · {{ membership?.role }}</div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div style="display: flex; justify-content: space-between; align-items: center; gap: 8px; margin-bottom: 8px;">
          <div style="font-weight: 600;">
            Notifications
            <span v-if="unreadCount > 0" class="muted" style="font-weight: 400; font-size: 13px;">
              ({{ unreadCount }} unread)
            </span>
          </div>
          <button
            v-if="notifications.length"
            type="button"
            class="btn"
            style="padding: 4px 10px; font-size: 12px;"
            :disabled="notifBusy"
            @click="markAllRead"
          >
            Mark all read
          </button>
        </div>
        <div v-if="notifError" class="muted" style="color: #991b1b; font-size: 13px; margin-bottom: 8px;">
          {{ notifError }}
        </div>
        <div v-if="!notifications.length" class="muted" style="font-size: 13px;">
          No notifications yet.
        </div>
        <div
          v-for="n in notifications"
          :key="n.id"
          style="padding: 10px 0; border-top: 1px solid var(--jp-border);"
          :style="n.status !== 'read' ? { background: 'rgba(37, 99, 235, 0.04)' } : undefined"
        >
          <div style="display: flex; justify-content: space-between; gap: 8px;">
            <div style="font-weight: 600; font-size: 14px;">{{ n.title }}</div>
            <button
              v-if="n.status !== 'read'"
              type="button"
              class="btn"
              style="padding: 2px 8px; font-size: 11px; flex-shrink: 0;"
              @click="markRead(n.id)"
            >
              Read
            </button>
          </div>
          <div class="muted" style="font-size: 13px; margin-top: 4px;">{{ n.body }}</div>
          <button
            v-if="jobIdFrom(n)"
            type="button"
            class="btn"
            style="margin-top: 8px; padding: 4px 10px; font-size: 12px;"
            @click="openJob(n)"
          >
            Open job
          </button>
        </div>
      </div>

      <div class="card" style="margin-bottom: 12px;">
        <div style="font-weight: 600; margin-bottom: 8px;">Permissions</div>
        <ul class="muted" style="margin: 0; padding-left: 18px; line-height: 1.6;">
          <li>Create jobs: {{ yesNo(permissions?.can_create_jobs) }}</li>
          <li>Approve / publish: {{ yesNo(permissions?.can_approve_and_publish) }}</li>
          <li>Manage team: {{ yesNo(permissions?.can_manage_team) }}</li>
        </ul>
      </div>

      <div
        v-if="permissions?.can_approve_and_publish"
        class="card"
        style="margin-bottom: 12px;"
      >
        <div style="font-weight: 600; margin-bottom: 6px;">Social accounts</div>
        <p class="muted" style="margin: 0 0 12px; font-size: 13px;">
          Connect accounts for the single Publish action on a job. MVP uses a mock provider.
        </p>
        <div v-if="connError" class="muted" style="color: #991b1b; font-size: 13px; margin-bottom: 8px;">
          {{ connError }}
        </div>
        <div v-if="!connections.length" class="muted" style="font-size: 13px; margin-bottom: 10px;">
          No accounts connected yet.
        </div>
        <div
          v-for="c in connections"
          :key="c.id"
          style="display: flex; justify-content: space-between; align-items: center; gap: 8px; padding: 8px 0; border-top: 1px solid var(--jp-border);"
        >
          <div>
            <div style="font-weight: 600; font-size: 14px;">{{ c.display_name }}</div>
            <div class="muted" style="font-size: 12px;">{{ c.platform }} · {{ c.status }}</div>
          </div>
          <button
            v-if="c.status === 'active'"
            type="button"
            class="btn"
            style="padding: 6px 10px; font-size: 12px;"
            :disabled="connBusy"
            @click="disconnect(c.id)"
          >
            Disconnect
          </button>
        </div>
        <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 12px;">
          <button
            type="button"
            class="btn btn-primary"
            style="flex: 1; min-width: 120px;"
            :disabled="connBusy"
            @click="connect('facebook')"
          >
            Connect Facebook
          </button>
          <button
            type="button"
            class="btn btn-primary"
            style="flex: 1; min-width: 120px;"
            :disabled="connBusy"
            @click="connect('instagram')"
          >
            Connect Instagram
          </button>
        </div>
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
const pubConn = usePublishingConnections()
const notif = useNotifications()
const user = computed(() => auth.user.value)
const company = computed(() => auth.company.value)
const membership = computed(() => auth.membership.value)
const permissions = computed(() => auth.permissions.value)
const connections = computed(() => pubConn.connections.value)
const connBusy = computed(() => pubConn.busy.value)
const connError = computed(() => pubConn.error.value)
const notifications = computed(() => notif.items.value)
const unreadCount = computed(() => notif.unreadCount.value)
const notifBusy = computed(() => notif.busy.value)
const notifError = computed(() => notif.error.value)

function yesNo(v?: boolean) {
  return v ? 'Yes' : 'No'
}

function jobIdFrom(n: { metadata_json?: Record<string, unknown> | null }) {
  return notif.jobIdFrom(n as any)
}

async function markRead(id: string) {
  try {
    await notif.markRead(id)
  } catch {
    /* error in composable */
  }
}

async function markAllRead() {
  try {
    await notif.markAllRead()
  } catch {
    /* error in composable */
  }
}

async function openJob(n: { metadata_json?: Record<string, unknown> | null }) {
  const jobId = jobIdFrom(n)
  if (!jobId) return
  if (n && 'status' in n && (n as any).status !== 'read' && 'id' in n) {
    try {
      await notif.markRead((n as any).id)
    } catch {
      /* optional */
    }
  }
  await navigateTo(`/jobs/${jobId}`)
}

async function connect(platform: string) {
  try {
    await pubConn.start(platform)
  } catch {
    /* error in composable */
  }
}

async function disconnect(id: string) {
  if (!confirm('Disconnect this account?')) return
  try {
    await pubConn.disconnect(id)
  } catch {
    /* error in composable */
  }
}

onMounted(async () => {
  try {
    await notif.list()
  } catch {
    /* optional */
  }
  if (permissions.value?.can_approve_and_publish) {
    try {
      await pubConn.list()
    } catch {
      /* optional */
    }
  }
})
</script>
